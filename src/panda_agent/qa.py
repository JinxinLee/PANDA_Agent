"""M5 bounded LangGraph QA with claim-level evidence verification."""

from __future__ import annotations

from copy import deepcopy
import json
import re
import time
from pathlib import Path
from typing import Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph

from panda_agent.llm.vertex import VertexAIClient, VertexSettings
from panda_agent.models import ClaimCitation, Evidence, QAResult, QAStatus, RetrievalPlan, stable_id
from panda_agent.prompts import (
    ANSWER_COMPOSER_REVIEW_SYSTEM_PROMPT,
    ANSWER_COMPOSER_SYSTEM_PROMPT,
    ANSWER_SYSTEM_PROMPT,
    ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT,
    ANSWER_POINT_COVERAGE_REVISION_SYSTEM_PROMPT,
    PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SYSTEM_PROMPT,
    PRODUCTION_COVERAGE_SATISFACTION_REVISION_SYSTEM_PROMPT,
    EVIDENCE_REVIEW_SYSTEM_PROMPT,
    REVISION_SYSTEM_PROMPT,
)
from panda_agent.question_decomposition import QuestionDecomposer
from panda_agent.retrieval import Retriever

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string"},
                    "claim_text": {"type": "string"},
                    "evidence_ids": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                    "answer_point_ids": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string"},
                    },
                },
                "required": ["claim_id", "claim_text", "evidence_ids", "answer_point_ids"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["claims"],
    "additionalProperties": False,
}
REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "supported": {"type": "boolean"},
        "unsupported_claim_ids": {"type": "array", "items": {"type": "string"}},
        "irrelevant_claim_ids": {"type": "array", "items": {"type": "string"}},
        "missing_requirement_ids": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
    },
    "required": ["supported", "unsupported_claim_ids", "irrelevant_claim_ids", "missing_requirement_ids", "reason"],
    "additionalProperties": False,
}


RUNTIME_ANSWER_POINT_ID = "question_core"


def _normalise_rejected_identifier_token(token: str) -> str:
    """Remove terminal prose punctuation without consuming a scope operator."""
    token = token.rstrip(".")
    if token.endswith(":") and not token.endswith("::"):
        token = token[:-1]
    return token


_CODE_DATA_EXTENSIONS = (".C", ".py", ".root", ".h", ".hpp", ".cpp", ".cxx", ".json", ".txt", ".yaml", ".yml")


DEFAULT_ANSWER_POINT_MODE = "production_answer_obligations_v1"


def _is_public_claim_citation_eligible(evidence: dict[str, Any]) -> bool:
    """Apply the existing Sphinx citation contract at claim evidence admission."""
    if "sphinx" in evidence["source_id"]:
        locator = evidence.get("locator") or {}
        return bool(locator.get("url") and locator.get("snapshot_date") and locator.get("section_path"))
    return True


def _normalized_claim_text(text: Any) -> str:
    """Case/whitespace/punctuation-insensitive form for claim restatement checks."""
    return re.sub(r"[\W_]+", "", str(text or "").casefold())


def _evidence_source_types(item: dict[str, Any]) -> set[str]:
    """Single shared source-type classifier (sufficiency + requirement backstop).

    Centralized so the sufficiency gate and the legacy source-role-grounding
    backstop can never diverge on what kind of source an evidence item is.
    """
    source_types: set[str] = set()
    source_id = str(item.get("source_id") or "")
    if source_id in {"li_2026", "karavdina_2015", "pflueger_2017"}:
        source_types.add("paper")
    elif "sphinx" in source_id:
        source_types.add("documentation")
    elif str((item.get("locator") or {}).get("path") or "").replace("\\", "/").lower().startswith(("docs/", "doc/")):
        source_types.add("documentation")
    else:
        source_types.add("code")
        path = str((item.get("locator") or {}).get("path") or "")
        if path.lower().split("/")[-1].startswith("readme"):
            source_types.add("readme")
        if item.get("object_type") in {"workflow", "python_script", "shell_script"}:
            source_types.add("workflow")
    source_types.update(channel for channel in item.get("retrieval_channels", []) if channel in {"workflow", "graph"})
    return source_types


_ANSWER_POINT_MODES = {
    "legacy_question_core",
    "shadow_e1_v2",
    "runtime_e1_v2",
    "production_answer_obligations_v1",
}
ANSWER_POINT_COVERAGE_REVIEW_SCHEMA = {
    **REVIEW_SCHEMA,
    "properties": {
        **REVIEW_SCHEMA["properties"],
        "claim_answer_point_mappings": {
            "type": "array", "items": {
                "type": "object", "properties": {
                    "claim_id": {"type": "string"},
                    "answer_point_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["claim_id", "answer_point_ids"], "additionalProperties": False,
            },
        },
        "missing_answer_point_ids": {"type": "array", "items": {"type": "string"}},
        "answer_point_coverage": {
            "type": "array", "items": {
                "type": "object", "properties": {
                    "answer_point_id": {"type": "string"},
                    "supporting_claim_ids": {"type": "array", "items": {"type": "string"}},
                    "complete": {"type": "boolean"},
                },
                "required": ["answer_point_id", "supporting_claim_ids", "complete"],
                "additionalProperties": False,
            },
        },
    },
    "required": [*REVIEW_SCHEMA["required"], "claim_answer_point_mappings", "missing_answer_point_ids", "answer_point_coverage"],
}
COVERAGE_SATISFACTION_SCHEMA_VERSION = "coverage-satisfaction-v1"
PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA = deepcopy(ANSWER_POINT_COVERAGE_REVIEW_SCHEMA)
_C1_CHECK_PROPERTIES = {
    "relationship_text": {"type": "string"},
    "necessity_reason": {"type": "string"},
    "basis": {"type": "array", "maxItems": 2, "items": {
        "type": "object", "properties": {
            "evidence_id": {"type": "string"},
            "quote": {"type": "string"}},
        "required": ["evidence_id", "quote"], "additionalProperties": False}},
    "supporting_claim_ids": {"type": "array", "maxItems": 8, "items": {"type": "string"}},
    "satisfied": {"type": "boolean"},
    "admission_state": {"type": "string", "enum": ["ADMITTED_BACKING_AVAILABLE",
        "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING", "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE"]},
}
_C1_POINT_PROPERTIES = {
    "answer_point_id": {"type": "string"},
    "supporting_claim_ids": {"type": "array", "maxItems": 32, "items": {"type": "string"}},
    "complete": {"type": "boolean"},
    "scope_status": {"type": "string", "enum": ["ESTABLISHED", "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE", "OVERFLOW"]},
    "relationship_checks": {"type": "array", "maxItems": 4, "items": {
        "type": "object", "properties": _C1_CHECK_PROPERTIES,
        "required": list(_C1_CHECK_PROPERTIES), "additionalProperties": False}},
}
PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA["properties"]["answer_point_coverage"] = {
    "type": "array", "minItems": 1, "maxItems": 5, "items": {
        "type": "object", "properties": _C1_POINT_PROPERTIES,
        "required": list(_C1_POINT_PROPERTIES), "additionalProperties": False}}
C1_INCOMPLETE_NOTICE = "The available citable evidence does not establish a complete answer to this request."


def _coverage_satisfaction_enabled(state: Any) -> bool:
    return state.get("answer_point_coverage_mode") == "production_answer_obligations_v1"


COMPOSER_SCHEMA = {
    "type": "object",
    "properties": {
        "paragraphs": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "source_claim_ids": {"type": "array", "minItems": 1, "items": {"type": "string"}},
                },
                "required": ["text", "source_claim_ids"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["paragraphs"],
    "additionalProperties": False,
}
COMPOSER_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "valid": {"type": "boolean"},
        "unsupported_paragraph_indexes": {"type": "array", "items": {"type": "integer"}},
        "missing_or_distorted_claim_ids": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
    },
    "required": ["valid", "unsupported_paragraph_indexes", "missing_or_distorted_claim_ids", "reason"],
    "additionalProperties": False,
}
_INTERNAL_CLAIM_IDS = frozenset({"required_workflow", "required_code"})
_INTERNAL_CLAIM_PREFIXES = ("scope_", "dataflow_locator_")
_INTERNAL_CLAIM_TEXT_MARKERS = ("curated_panda_domain",)


_FUTURE_RUNTIME_TERMS = (
    "future", "next run", "will run", "after running", "when run", "upcoming",
    "未来", "下次运行", "将运行", "运行后", "执行后",
)
_EXACT_RESULT_TERMS = (
    "exact", "precise", "deterministic", "checksum", "hash", "sha256", "sha-256",
    "md5", "digest", "精确", "确切", "校验和", "哈希", "摘要",
)
_RUNTIME_ARTIFACT_TERMS = (
    "runtime", "run", "execution", "output", "result", "artifact", "file produced",
    "event", "运行", "执行", "输出", "结果", "产物", "事件",
)
_UNIVERSAL_PROOF_TERMS = (
    "prove", "proof", "theorem", "for all", "every", "any", "universal",
    "证明", "定理", "对所有", "所有", "任意", "普遍",
)
_FORMAL_PROOF_TERMS = (
    "theorem", "proof", "lemma", "proposition", "corollary",
    "定理", "证明", "引理", "命题", "推论",
)
_FINITE_EVALUATION_TERMS = (
    "finite", "evaluated", "evaluation", "case", "cases", "sample", "simulation",
    "validated", "validation", "test", "tested", "有限", "评估", "案例", "样本", "模拟", "验证",
)
_CONVERGENCE_VALIDATION_TERMS = (
    "converg", "iteration", "iterative", "contracting map", "stability",
    "收敛", "迭代", "稳定",
)
_PAPER_SOURCE_IDS = frozenset({"li_2026", "karavdina_2015", "pflueger_2017"})
_ANSWER_REQUIREMENT_TERMS = {
    "workflow_order": (
        "workflow", "sequence", "order", "pipeline", "step", "流程", "顺序", "步骤",
    ),
    "factory_composition": (
        "factory", "composition", "compose", "construct", "constructor", "setter", "input", "output",
        "工厂", "组合", "构造", "设置器", "输入", "输出",
    ),
    "troubleshooting": (
        "troubleshoot", "debug", "diagnose", "failure", "fails", "not work", "error",
        "排查", "调试", "诊断", "失败", "不工作", "错误",
    ),
}


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _question_domain_tokens(question: str) -> set[str]:
    """Extract conservative domain anchors for formal-proof evidence checks."""
    ignored = {
        "prove", "proof", "theorem", "for", "all", "every", "any", "universal",
        "that", "this", "with", "from", "does", "can", "will", "the", "and",
        "algorithm", "input", "inputs", "property", "properties", "invariant",
        "possible", "works", "work", "system", "code", "program",
    }
    return {
        token.casefold()
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_:-]{2,}", question)
        if token.casefold() not in ignored
    }


def _has_same_domain_formal_proof(question: str, evidence: list[dict[str, Any]]) -> bool:
    """Accept universal requests only when the corpus supplies a matching proof."""
    anchors = _question_domain_tokens(question)
    for item in evidence:
        text = " ".join(
            (
                str(item.get("text") or ""),
                str((item.get("locator") or {}).get("symbol") or ""),
                str((item.get("locator") or {}).get("path") or ""),
            )
        ).casefold()
        if not _contains_any(text, _FORMAL_PROOF_TERMS):
            continue
        if anchors and any(anchor in text for anchor in anchors):
            return True
    return False


def _evidence_search_text(item: dict[str, Any]) -> str:
    """Return only evidence-backed fields usable for deterministic relevance."""
    locator = item.get("locator") or {}
    return " ".join(
        str(value or "")
        for value in (
            item.get("text"),
            locator.get("path"),
            locator.get("symbol"),
            " ".join(locator.get("section_path") or []),
            item.get("source_id"),
        )
    ).casefold()


def _is_theory_or_paper_evidence(item: dict[str, Any]) -> bool:
    return (
        str(item.get("source_id") or "") in _PAPER_SOURCE_IDS
        or str(item.get("object_type") or "").casefold() in {"paper", "theory", "publication"}
    )


def _is_code_or_workflow_evidence(item: dict[str, Any]) -> bool:
    if _is_theory_or_paper_evidence(item):
        return False
    object_type = str(item.get("object_type") or "").casefold()
    channels = {str(value).casefold() for value in item.get("retrieval_channels", [])}
    path = str((item.get("locator") or {}).get("path") or "")
    return (
        object_type in {"class", "function", "method", "workflow", "python_script", "shell_script", "macro"}
        or bool(path)
        or bool(channels & {"workflow", "graph", "exact"})
    )


def _refusal_basis_evidence(
    state: QAState, *, kind: str
) -> dict[str, Any] | None:
    """Select one relevant, cited basis for a conservative refusal.

    This is deliberately a ranking over the existing retrieval bundle: it
    never adds evidence, invents a source, or uses benchmark metadata.
    """
    question = str(state.get("question") or "")
    plan = state.get("bundle", {}).get("plan", {})
    evidence = list(state.get("bundle", {}).get("evidence", []))
    # Question-only anchors are the relevance authority for the
    # unsupported_symbol kind: a plan-only suggestion must never make
    # unrelated evidence look like a refusal basis (F2-A4-R1).
    question_anchors = _question_domain_tokens(question)
    anchors = set(question_anchors)
    for value in [*plan.get("symbols", []), *plan.get("concepts", [])]:
        anchors.update(_question_domain_tokens(str(value)))
    question_text = question.casefold()

    plan_anchor_text = " ".join(
        str(value)
        for value in (
            [*plan.get("symbols", []), *plan.get("concepts", [])]
            + list((plan.get("concept_scopes") or {}).keys())
            + list((plan.get("concept_scopes") or {}).values())
        )
    ).casefold()

    if kind == "future_runtime":
        candidates = [item for item in evidence if _is_code_or_workflow_evidence(item)]
        preferred_terms = _RUNTIME_ARTIFACT_TERMS
    elif kind == "universal_proof":
        candidates = [
            item
            for item in evidence
            if _is_theory_or_paper_evidence(item)
            and _contains_any(
                _evidence_search_text(item),
                _FINITE_EVALUATION_TERMS + _CONVERGENCE_VALIDATION_TERMS,
            )
        ]
        preferred_terms = _FINITE_EVALUATION_TERMS
    elif kind == "unsupported_symbol":
        # The locked-catalog absence is the refusal authority.  Selected
        # evidence may at most supply a narrow, cited, query-relevant context
        # statement; relevance is judged by question-only anchors, so plan-only
        # symbols/concepts cannot admit unrelated evidence.
        candidates = [
            item
            for item in evidence
            if _is_code_or_workflow_evidence(item)
            and any(anchor in _evidence_search_text(item) for anchor in question_anchors)
        ]
        preferred_terms = ()
    elif kind == "deleted_runtime":
        # Deleted-runtime context may only cite already-selected code/workflow
        # evidence that explicitly overlaps an identifier-like artifact anchor
        # from the live question (e.g. event_poca, sensor_hits).  Generic prose
        # overlap never qualifies, and no historical path receives preference.
        artifact_anchors = {token for token in question_anchors if "_" in token}
        candidates = [
            item
            for item in evidence
            if _is_code_or_workflow_evidence(item)
            and any(anchor in _evidence_search_text(item) for anchor in artifact_anchors)
        ]
        preferred_terms = ()
    else:
        raise ValueError(f"unknown refusal basis kind: {kind}")
    if not candidates:
        return None

    def score(item: dict[str, Any]) -> tuple[int, str]:
        text = _evidence_search_text(item)
        ranking_anchors = question_anchors if kind in {"unsupported_symbol", "deleted_runtime"} else anchors
        overlap = sum(anchor in text for anchor in ranking_anchors)
        shared_request_terms = sum(
            term in question_text and term in text for term in preferred_terms
        )
        locator = item.get("locator") or {}
        path = str(locator.get("path") or "").casefold()
        symbol = str(locator.get("symbol") or "").casefold()
        object_type = str(item.get("object_type") or "").casefold()
        source_id = str(item.get("source_id") or "").casefold()
        if kind == "future_runtime":
            # Prefer the exact executable/producer named in the active plan.
            # A README or Sphinx mention is still a usable fallback, but cannot
            # outrank an exact locked macro/script/function that produces the
            # requested runtime artifact.
            exact_plan_anchor = any(
                token and token in text
                for token in (path, symbol)
                if token and token in plan_anchor_text
            )
            executable_or_producer = (
                path.endswith((".py", ".sh", ".c", ".cc", ".cpp", ".cxx"))
                or object_type in {"function", "method", "macro", "python_script", "shell_script", "workflow"}
                or any(term in text for term in ("write", "writes", "produce", "produces", "generate", "creates"))
            )
            documentation = (
                "sphinx" in source_id
                or "readme" in path
                or object_type in {"documentation", "readme", "sphinx_page"}
            )
            source_preference = 1000 * int(exact_plan_anchor) + 200 * int(executable_or_producer) - 100 * int(documentation)
        elif kind in {"unsupported_symbol", "deleted_runtime"}:
            # Rank purely by query-anchor overlap; no source-type or path
            # preference, so no historical locator receives special treatment.
            source_preference = 100 * overlap
        else:
            # A refusal of an open-domain proof should cite the closest
            # query-specific finite validation or convergence result, rather
            # than a generic paper mention.
            query_specific = 100 * overlap
            finite_limit = 50 * sum(term in text for term in _FINITE_EVALUATION_TERMS)
            convergence_or_iteration = 300 * sum(
                term in text for term in _CONVERGENCE_VALIDATION_TERMS
            )
            source_preference = 200 * int(_is_theory_or_paper_evidence(item)) + query_specific + finite_limit + convergence_or_iteration
        return (source_preference + shared_request_terms, str(item.get("evidence_id") or ""))

    # ``min`` keeps the stable evidence ID as deterministic final tie-breaker.
    return min(candidates, key=lambda item: (-score(item)[0], score(item)[1]))


def _refusal_basis_location(item: dict[str, Any]) -> str:
    locator = item.get("locator") or {}
    return str(locator.get("path") or locator.get("symbol") or item.get("source_id") or "the cited source")


def _is_class_shaped_identifier(token: str) -> bool:
    """Compound-cased identifier shape; plain capitalized prose is excluded."""
    return (
        len(token) >= 2
        and token[0].isupper()
        and any(
            token[i].islower() and token[i + 1].isupper()
            for i in range(len(token) - 1)
        )
    )


_REQUESTED_SYMBOL_CONTEXT_TERMS = (
    "how does", "how should", "how is", "what does",
    "where is", "where's", "which file", "which code", "path",
    "defined", "implemented", "implement",
)


def _is_code_like_identifier(token: str) -> bool:
    """Bounded plausibility check for an explicit class/struct/enum token.

    Accepts identifiers that are plausibly code (initially capitalized or
    underscore-bearing); rejects ordinary lowercase prose continuations such
    as "of", "layout", or "type".
    """
    return len(token) > 2 and (token[0].isupper() or "_" in token)


def _requested_bare_class_symbols(question: str) -> list[str]:
    """Extract code symbols the user question itself requests or assumes.

    Bounded question-grounded sources only:

    * explicit ``class Foo`` / ``struct Foo`` / ``enum Foo`` wording;
    * pointer type expressions such as ``Foo*``;
    * class-shaped (compound-cased) identifiers named inside a
      request/definition context such as "How does X ...", "Where is X
      defined", so ordinary capitalized prose words never become requested
      classes.

    The caller checks the locked-corpus catalog; retrieval-plan symbols are
    never consulted, so a plan-only symbol can never create a refusal.
    """
    candidates: list[str] = []
    seen: set[str] = set()

    def add(name: str) -> None:
        if name and name not in seen:
            seen.add(name)
            candidates.append(name)

    for match in re.finditer(r"\b(?:class|struct|enum)\s+([A-Za-z_][A-Za-z0-9_]*)", question):
        token = match.group(1)
        # Natural-language continuations ("class of", "struct layout") are not
        # code symbols; require a plausible identifier shape.
        if _is_code_like_identifier(token):
            add(token)
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\*", question):
        token = match.group(1)
        if _is_code_like_identifier(token):
            add(token)
    if any(term in question.casefold() for term in _REQUESTED_SYMBOL_CONTEXT_TERMS):
        for match in re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*\b", question):
            token = match.group(0)
            if _is_class_shaped_identifier(token):
                add(token)
    return candidates


def _refusal_basis_subject(question: str, item: dict[str, Any]) -> str:
    """Name a query-overlapping domain anchor without inventing a subject."""
    text = _evidence_search_text(item)
    matches = sorted(
        (anchor for anchor in _question_domain_tokens(question) if anchor in text),
        key=lambda anchor: (-len(anchor), anchor),
    )
    return matches[0] if matches else "the requested artifact or domain"


def _answer_requirements(question: str, plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Derive answer-completeness obligations from the live question and plan.

    These are generation/review instructions, not benchmark answer points.  They
    intentionally describe response shape only and never encode an expected
    repository-specific conclusion.
    """
    text = question.casefold()
    intent = str(plan.get("intent") or "").casefold()
    plan_text = " ".join(
        str(value)
        for value in (
            [*plan.get("symbols", []), *plan.get("concepts", []), *plan.get("required_source_types", [])]
            + list((plan.get("concept_scopes") or {}).keys())
            + list((plan.get("concept_scopes") or {}).values())
        )
    ).casefold()
    required_source_types = {
        str(value).casefold() for value in plan.get("required_source_types", [])
    }
    requirements: list[dict[str, str]] = []

    def add(requirement_id: str, instruction: str) -> None:
        requirements.append({"id": requirement_id, "instruction": instruction})

    event_alignment_question = (
        intent == "data_flow"
        and _contains_any(text, ("event id", "event_id"))
        and "pid" in text
        and not _contains_any(text, _ANSWER_REQUIREMENT_TERMS["workflow_order"])
    )
    workflow_triggered = (
        intent in {"workflow", "data_flow", "lifecycle"}
        or _contains_any(text, _ANSWER_REQUIREMENT_TERMS["workflow_order"])
    ) and not event_alignment_question
    if workflow_triggered:
        add(
            "workflow_order",
            "State the evidence-backed stages in execution order; when a middle stage is discussed, include its predecessor and successor when supplied evidence establishes them.",
        )
    if intent == "data_flow" or (workflow_triggered and _contains_any(text, ("handoff", "data flow", "transfer", "传递", "衔接"))):
        add(
            "complete_dataflow_handoff",
            "Describe each evidence-backed handoff completely: producer, named intermediate input/product, and next consumer, including a second hop when the question asks for downstream flow.",
        )

    module_mapping_question = (
        intent == "module_structure"
        and _contains_any(text, ("map ", " vs ", "directory", "directories", "folder", "目录", "文件夹"))
        and not _contains_any(text, ("construct", "compose", "composition", "setter", "build", "构造", "组合", "设置器"))
    )
    explicit_factory_triggered = not module_mapping_question and _contains_any(
        text,
        ("factory", "composition", "compose", "construct", "constructor", "setter", "工厂", "组合", "构造", "设置器"),
    ) or (
        _contains_any(text, ("input", "输入"))
        and _contains_any(text, ("output", "输出"))
        and _contains_any(text, ("create", "build", "make", "生成", "创建"))
    )
    plan_factory_triggered = (
        intent in {"algorithm_implementation", "api", "data_flow", "module_structure"}
        and not module_mapping_question
        and _contains_any(plan_text, ("factory", "setacceptance", "generate2dmodel"))
    )
    factory_triggered = explicit_factory_triggered or plan_factory_triggered
    if factory_triggered:
        add(
            "factory_composition",
            "For a composition or factory question, trace the evidence-backed chain from input and configuration/setter through construction or factory selection to the produced object or output; do not merely list components.",
        )
        if _contains_any(plan_text, ("divergence", "smearing")):
            add(
                "divergence_factory_composition",
                "Explain how an evidence-backed divergence or smearing component enters the factory/model-construction path and becomes part of the resulting fit model, not only how the component internally computes a map.",
            )
        if _contains_any(plan_text, ("acceptance", "pndlmdacceptance", "setacceptance")):
            add(
                "acceptance_factory_application",
                "Explain both storage/configuration of acceptance data and the evidence-backed construction point where the factory applies that stored acceptance to the resulting model; do not stop at the setter declaration.",
            )

    profile_terms = ("longitudinal", "restgas profile", "restgas_profile", "纵向", "restgas")
    angular_acceptance_terms = ("angular", "acceptance", "pndlmdacceptance", "角向", "接受度")
    profile_in_plan = _contains_any(plan_text, ("longitudinal_profile", "longitudinal", "restgas profile", "restgas_profile", "纵向"))
    angular_in_plan = _contains_any(plan_text, ("angular", "acceptance", "pndlmdacceptance", "角向", "接受度"))
    if (_contains_any(text, profile_terms) and _contains_any(text, angular_acceptance_terms)) or (profile_in_plan and angular_in_plan):
        add(
            "longitudinal_vs_angular_acceptance",
            "Make the boundary explicit: contrast the longitudinal profile or efficiency role with the angular acceptance role, and do not collapse them into one correction.",
        )

    dpm_luminosity_triggered = (
        _contains_any(text + " " + plan_text, ("elastic", "differential cross section", "differential cross-section"))
        and _contains_any(text + " " + plan_text, ("luminosity",))
        and _contains_any(text + " " + plan_text, ("fit", "fitting", "measured distribution", "distribution"))
    ) or (
        _contains_any(text + " " + plan_text, ("dpm", "ana_dpm"))
        and _contains_any(text + " " + plan_text, ("elastic", "differential cross section", "differential cross-section"))
        and _contains_any(text, ("represent", "purpose", "describe", "what does", "meaning", "表示", "用途", "描述"))
    )
    if dpm_luminosity_triggered:
        add(
            "elastic_cross_section_luminosity_fit",
            "Connect the evidence-backed elastic differential-cross-section theory input to fitting the measured distribution and extracting luminosity; do not describe the theory or fit in isolation.",
        )

    # F6-A2-FR2-R1: when the question itself calls for more than one source
    # role, legacy answers ground each part of the explanation in the source
    # kind that actually supports it.  This is a user-relevant content
    # requirement carried by the existing requirement contract — it never
    # synthesizes a public provenance mention, and coverage modes (which
    # receive no legacy requirements) are unaffected (F2-A3-R1).
    if len(required_source_types) >= 2:
        requirements.append(
            {
                "id": "source_role_grounding",
                "instruction": (
                    "Where selected evidence covers more than one of the source kinds the "
                    "question calls for, ground each part of the explanation in the kind of "
                    "source that actually supports it, so every cited source backs a "
                    "substantive, user-relevant part of the answer; do not add "
                    "provenance-only or coverage-only statements merely to mention a source kind."
                ),
                "required_source_types": sorted(required_source_types),
            }
        )

    reader_selection_triggered = (
        "pndlmddatareader" in plan_text
        and _contains_any(
            text + " " + plan_text,
            ("selection", "filter", "accepted", "generated", "histogram", "efficiency"),
        )
    )
    if reader_selection_triggered:
        add(
            "reader_selection_histogram_accounting",
            "For a data-reader efficiency/accounting question, inspect the evidence-backed selection or filter conditions and the accepted-versus-generated histogram filling; do not stop at tree or branch assumptions.",
        )

    pointer_type_match = re.search(r"[A-Za-z_][A-Za-z0-9_:]*\*", question)
    pointer_normalization_triggered = (
        pointer_type_match
        and _contains_any(text + " " + plan_text, ("pointer", "type expression", "normalize", "normalization"))
    )
    if pointer_normalization_triggered:
        requirements.append({
            "id": "pointer_identifier_normalization",
            "instruction": "State the identifier normalization explicitly: remove pointer/reference syntax from the type expression, name the underlying code symbol, and say that the qualifier is not part of a new identifier before explaining where the symbol is consumed.",
            "target_symbol": pointer_type_match.group(0).rstrip("*"),
        })

    model_layer_inventory_triggered = (
        intent == "module_structure"
        and _contains_any(text + " " + plan_text, ("model layer", "model-layer", "模型层"))
        and _contains_any(plan_text, ("dpm", "cross section", "physics model"))
        and _contains_any(plan_text, ("smearing", "resolution", "divergence"))
        and _contains_any(plan_text, ("modelfactory", "model factory"))
    )
    if model_layer_inventory_triggered:
        add(
            "model_layer_component_inventory",
            "Inventory all evidence-backed model-layer roles: DPM/physics, acceptance, detector-resolution or divergence smearing, and the model factory that assembles them. Do not omit acceptance merely because it is configured or applied by the factory.",
        )

    implementation_disambiguation_triggered = (
        intent in {"troubleshooting", "debugging"}
        and (
            _contains_any(text, ("class name match", "name match", "wrong implementation", "same-named", "same named"))
            or (
                _contains_any(plan_text, ("class name matching", "implementation ambiguity"))
                and _contains_any(plan_text, ("code retrieval", "disambiguation"))
            )
        )
    )
    if implementation_disambiguation_triggered:
        add(
            "implementation_disambiguation_procedure",
            "Explain that a name match is insufficient. Resolve source/repository and full path, enforce the locked revision internally when version or fork identity matters, then inspect the implementation, callers/configuration sites, and consumed or produced data products before accepting the match. Do not invent an implementation difference that the cited evidence does not show.",
        )

    troubleshooting_triggered = intent in {"troubleshooting", "debugging"} or _contains_any(
        text, _ANSWER_REQUIREMENT_TERMS["troubleshooting"]
    )
    if troubleshooting_triggered and not implementation_disambiguation_triggered:
        add(
            "troubleshoot_upstream_to_downstream",
            "Troubleshoot upstream first: inspect input, then producer, then consumer; check binning, range, and schema compatibility wherever those interfaces are evidenced.",
        )
        if _contains_any(text + " " + plan_text, ("empty bin", "empty-bin", "binning", "range", "efficiency", "profile", "compatibility", "空 bin", "空bin", "分箱", "范围", "效率", "兼容")):
            add(
                "explicit_compatibility_check",
                "State the evidence-backed empty-bin, binning, profile-range, or efficiency compatibility condition explicitly; do not replace it with a generic troubleshooting conclusion.",
            )
        empty_bin_diagnosis_triggered = _contains_any(
            text, ("empty bin", "empty-bin", "空 bin", "空bin")
        ) or (
            _contains_any(plan_text, ("empty bin", "empty-bin", "空 bin", "空bin"))
            and not _contains_any(
                text,
                ("accepted/generated", "accepted and generated", "histogram filling", "selection filters"),
            )
        )
        if empty_bin_diagnosis_triggered and _contains_any(
            text + " " + plan_text, ("efficiency", "profile", "denominator")
        ):
            add(
                "efficiency_empty_bin_diagnosis",
                "Explain whether numerator-empty bins arise from reconstructed selection or migration, handle denominator-zero efficiency explicitly, and check the binning/profile compatibility; do not diagnose only one side of the ratio.",
            )
    if intent == "data_flow" and required_source_types & {"workflow", "documentation"}:
        add(
            "workflow_or_operational_grounding",
            "Include a user-relevant factual workflow or operational-documentation claim that explains a concrete stage, handoff, or procedure; never expose retrieval metadata or coverage labels.",
        )
    return requirements


def _internal_claim_reason(claim: dict[str, Any]) -> str | None:
    """Return the diagnostic-only reason for synthetic/internal claims.

    Retrieval provenance and coverage bookkeeping are useful to audit an
    answer, but they are not facts the user asked the agent to explain.  Keep
    these identifiers out of the public answer even when their evidence is
    valid.  The text-marker check also protects against a model echoing an
    internal workflow source name under a different claim ID.
    """
    claim_id = str(claim.get("claim_id") or "")
    if claim_id in _INTERNAL_CLAIM_IDS:
        return f"internal_claim_id:{claim_id}"
    if any(claim_id.startswith(prefix) for prefix in _INTERNAL_CLAIM_PREFIXES):
        return f"internal_claim_prefix:{claim_id}"
    claim_text = str(claim.get("claim_text") or "").casefold()
    if any(marker in claim_text for marker in _INTERNAL_CLAIM_TEXT_MARKERS):
        return "internal_metadata_text"
    return None


def _runtime_answer_points(question: str) -> list[dict[str, str]]:
    """Construct a non-benchmark answer objective from the current question."""
    return [{"answer_point_id": RUNTIME_ANSWER_POINT_ID, "text": question}]


def _coverage_shadow(state: QAState) -> bool:
    return state.get("answer_point_coverage_mode") in {
        "shadow_e1_v2",
        "runtime_e1_v2",
        "production_answer_obligations_v1",
    }


def _active_runtime_answer_points(state: QAState) -> list[dict[str, str]]:
    if not _coverage_shadow(state):
        return _runtime_answer_points(str(state.get("question", "")))
    points = state.get("runtime_answer_points")
    if not isinstance(points, list) or not points:
        raise ValueError("shadow answer points must be a non-empty list")
    projected = []
    seen = set()
    for point in points:
        if not isinstance(point, dict) or any(
            not isinstance(point.get(k), str) or not point[k].strip()
            for k in ("answer_point_id", "text")
        ) or point["answer_point_id"] in seen:
            raise ValueError("shadow answer points require unique non-empty IDs and texts")
        seen.add(point["answer_point_id"])
        projected.append({k: point[k] for k in ("answer_point_id", "text")})
    return projected


def _model_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Project model-facing claims; private provenance cannot be model-authored."""
    return [{k: c.get(k) for k in ("claim_id", "claim_text", "evidence_ids", "answer_point_ids")}
            for c in claims]


def _validate_answer_point_review(
    review: Any, claims: list[dict[str, Any]], point_ids: set[str], requirement_ids: set[str]
) -> dict[str, list[str]]:
    """Validate semantic decisions without turning mapping presence into coverage."""
    def require(ok: bool, message: str) -> None:
        if not ok:
            raise ValueError(message)

    require(isinstance(review, dict) and set(review) == set(ANSWER_POINT_COVERAGE_REVIEW_SCHEMA["required"]),
            "invalid coverage review fields")
    require(type(review["supported"]) is bool and isinstance(review["reason"], str), "invalid review types")
    known = {c["claim_id"] for c in claims}
    def ids(value: Any, allowed: set[str]) -> list[str]:
        require(isinstance(value, list) and all(isinstance(v, str) for v in value), "review IDs must be strings")
        require(len(value) == len(set(value)) and set(value) <= allowed, "unknown or duplicate review ID")
        return value

    unsupported = set(ids(review["unsupported_claim_ids"], known))
    irrelevant = set(ids(review["irrelevant_claim_ids"], known))
    missing = set(ids(review["missing_answer_point_ids"], point_ids))
    ids(review["missing_requirement_ids"], requirement_ids)
    records = review["claim_answer_point_mappings"]
    require(isinstance(records, list), "mapping records must be a list")
    mappings = {}
    for record in records:
        require(isinstance(record, dict) and set(record) == {"claim_id", "answer_point_ids"}, "invalid mapping record")
        cid = record["claim_id"]
        require(isinstance(cid, str) and cid in known and cid not in mappings, "unknown or repeated mapping claim")
        mappings[cid] = ids(record["answer_point_ids"], point_ids)
        require(bool(mappings[cid]) or cid in unsupported | irrelevant, "unmapped claim must be unsupported or irrelevant")
    require(set(mappings) == known, "each reviewable claim requires one mapping")
    contributing = {pid for cid, values in mappings.items() if cid not in unsupported | irrelevant for pid in values}
    require(point_ids - missing <= contributing, "covered point lacks a supported relevant mapped claim")
    # Post-A5 completeness recovery: the reviewer must separately judge each
    # runtime point's completeness, so mapping relevance alone can never imply
    # coverage and contradictory review states fail deterministically.
    coverage = review["answer_point_coverage"]
    require(isinstance(coverage, list), "coverage records must be a list")
    covered_points: set[str] = set()
    complete_points: set[str] = set()
    for record in coverage:
        require(
            isinstance(record, dict)
            and set(record) == {"answer_point_id", "supporting_claim_ids", "complete"},
            "invalid coverage record",
        )
        pid = record["answer_point_id"]
        require(
            isinstance(pid, str) and pid in point_ids and pid not in covered_points,
            "unknown or repeated coverage point",
        )
        covered_points.add(pid)
        supporters = ids(record["supporting_claim_ids"], known)
        require(type(record["complete"]) is bool, "coverage complete flag must be boolean")
        for cid in supporters:
            require(cid not in unsupported | irrelevant, "unsupported or irrelevant claim cannot support a point")
            require(pid in mappings.get(cid, []), "supporting claim must map to the point")
        if record["complete"]:
            require(bool(supporters), "complete point requires supported contributing claims")
            complete_points.add(pid)
    require(covered_points == point_ids, "each runtime point requires exactly one coverage record")
    require(complete_points == point_ids - missing, "incomplete points must be exactly the missing points")
    return mappings


def _validate_coverage_satisfaction(
    review: Any, claims: list[dict[str, Any]], point_ids: set[str], requirement_ids: set[str],
    evidence: dict[str, dict[str, Any]], admitted_ids: set[str],
) -> dict[str, list[str]]:
    """Validate structure/provenance, never semantic necessity or entailment."""
    def require(ok: bool, message: str) -> None:
        if not ok:
            raise ValueError(message)

    require(isinstance(review, dict), "invalid production review")
    coverage = review.get("answer_point_coverage")
    require(isinstance(coverage, list) and 1 <= len(coverage) <= 5, "invalid production coverage count")
    for p in coverage:
        require(isinstance(p, dict) and set(p) == set(_C1_POINT_PROPERTIES), "invalid production point fields")
    legacy = {**review, "answer_point_coverage": [
        {k: p[k] for k in ("answer_point_id", "supporting_claim_ids", "complete")} for p in coverage]}
    mappings = _validate_answer_point_review(legacy, claims, point_ids, requirement_ids)
    claim_lookup = {c["claim_id"]: c for c in claims}
    excluded = set(review["unsupported_claim_ids"]) | set(review["irrelevant_claim_ids"])
    total = 0
    for p in coverage:
        status = p["scope_status"]
        require(isinstance(status, str) and status in _C1_POINT_PROPERTIES["scope_status"]["enum"], "invalid scope status")
        checks = p["relationship_checks"]
        require(isinstance(checks, list) and len(checks) <= 4, "relationship count exceeds point bound")
        total += len(checks)
        require(total <= 20, "relationship count exceeds question bound")
        require(len(p["supporting_claim_ids"]) <= 32, "point supporter bound exceeded")
        require(status != "ESTABLISHED" or bool(checks), "established scope requires checks")
        texts, union = set(), set()
        for check in checks:
            require(isinstance(check, dict) and set(check) == set(_C1_CHECK_PROPERTIES), "invalid relationship fields")
            for key, bound in (("relationship_text", 240), ("necessity_reason", 160)):
                value = check[key]
                require(isinstance(value, str) and bool(value.strip()) and len(value) <= bound, f"invalid {key}")
            normalized = " ".join(check["relationship_text"].split())
            require(normalized not in texts, "duplicate relationship text")
            texts.add(normalized)
            admission = check["admission_state"]
            require(isinstance(admission, str) and admission in _C1_CHECK_PROPERTIES["admission_state"]["enum"], "invalid admission state")
            require(type(check["satisfied"]) is bool, "satisfied must be boolean")
            basis = check["basis"]
            require(isinstance(basis, list) and len(basis) <= 2, "basis bound exceeded")
            basis_ids = set()
            for item in basis:
                require(isinstance(item, dict) and set(item) == {"evidence_id", "quote"}, "invalid basis fields")
                eid, quote = item["evidence_id"], item["quote"]
                require(isinstance(eid, str) and eid in evidence and eid not in basis_ids, "unknown or duplicate basis ID")
                require(isinstance(quote, str) and bool(quote.strip()) and len(quote) <= 400
                        and quote in evidence[eid].get("text", ""), "basis quote is not exact or exceeds bound")
                basis_ids.add(eid)
            supporters = check["supporting_claim_ids"]
            require(isinstance(supporters, list) and len(supporters) <= 8
                    and all(isinstance(c, str) for c in supporters), "invalid relationship supporters")
            require(len(set(supporters)) == len(supporters), "duplicate relationship supporter")
            for cid in supporters:
                require(cid in claim_lookup and cid not in excluded, "unknown unsupported or irrelevant supporter")
                require(p["answer_point_id"] in mappings[cid], "supporter maps to another point")
                require(basis_ids <= set(claim_lookup[cid].get("evidence_ids", [])), "supporter does not cite required basis")
            union.update(supporters)
            if admission == "ADMITTED_BACKING_AVAILABLE":
                require(bool(basis_ids) and basis_ids <= admitted_ids, "basis must be admitted")
                require(not check["satisfied"] or bool(supporters), "satisfied check requires supporters")
            else:
                require(not check["satisfied"] and not supporters, "uncitable or uncertain check cannot be satisfied")
                if admission == "VISIBLE_ONLY_WITHOUT_CITABLE_BACKING":
                    require(bool(basis_ids - admitted_ids), "visible-only check requires unadmitted basis")
            if status == "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE":
                require(admission == "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE", "uncertain scope requires uncertain checks")
            if admission == "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE":
                require(status == "INSUFFICIENT_OR_AMBIGUOUS_EVIDENCE", "uncertain check requires uncertain scope")
        require(p["supporting_claim_ids"] == [c["claim_id"] for c in claims if c["claim_id"] in union],
                "point supporters must equal ordered relationship union")
        complete = status == "ESTABLISHED" and bool(checks) and all(
            c["satisfied"] and c["admission_state"] == "ADMITTED_BACKING_AVAILABLE" for c in checks)
        require(p["complete"] == complete, "scope completeness mismatch")
    return mappings


def _normalise_claim_answer_points(
    claims: list[dict[str, Any]], question: str
) -> list[dict[str, Any]]:
    """Attach an internal answer-point mapping without changing public DTOs.

    The mapping is intentionally derived only from the current user question,
    never from benchmark Gold answer points.  Model-produced claims must carry
    their own non-empty schema-required mapping; this helper only ensures that
    synthetic internal claims have an explicit empty mapping for audit.
    """
    del question  # The stable runtime point ID represents the question itself.
    normalized: list[dict[str, Any]] = []
    for raw_claim in claims:
        claim = dict(raw_claim)
        if _internal_claim_reason(claim):
            claim["answer_point_ids"] = []
        normalized.append(claim)
    return normalized


def _abstract_external_type_text(text: str, allowed: str) -> str:
    """Abstract external wrappers while retaining balanced template payloads."""
    parts: list[str] = []
    cursor = 0
    pattern = re.compile(r"\b(?:boost|std)::[A-Za-z_][A-Za-z0-9_:]*")
    while match := pattern.search(text, cursor):
        parts.append(text[cursor:match.start()])
        end = match.end()
        opening = end
        while opening < len(text) and text[opening].isspace():
            opening += 1
        payload = None
        if opening < len(text) and text[opening] == "<":
            depth = 1
            end = opening + 1
            while end < len(text) and depth:
                depth += (text[end] == "<") - (text[end] == ">")
                end += 1
            if depth:
                # Do not manufacture a partial replacement for an incomplete type.
                parts.append(text[match.start():])
                return "".join(parts)
            payload = text[opening + 1:end - 1]
        if match.group().casefold() in allowed:
            parts.append(text[match.start():end])
        else:
            replacement = "an internal support type"
            if payload is not None and payload.strip():
                replacement += f" containing ({_abstract_external_type_text(payload, allowed)})"
            parts.append(replacement)
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts)


def _strip_nonessential_external_identifiers(
    claims: list[dict[str, Any]], question: str, plan: dict[str, Any]
) -> list[dict[str, Any]]:
    """Remove unrequested third-party implementation names from public claims.

    Evidence may contain implementation details such as Boost or STL helper
    types.  They are not a useful answer merely because they were retrieved,
    and often are not identifiers in the locked corpus.  Preserve such a name
    only when the user or the active plan explicitly asks for it.
    """
    allowed = " ".join(
        [question, *[str(value) for value in plan.get("symbols", [])]]
    ).casefold()
    cleaned: list[dict[str, Any]] = []
    for raw_claim in claims:
        claim = dict(raw_claim)
        text = str(claim.get("claim_text") or "")
        claim["claim_text"] = _abstract_external_type_text(text, allowed)
        cleaned.append(claim)
    return cleaned


def _is_workflow_evidence(item: dict[str, Any]) -> bool:
    """Recognize a concrete workflow object/channel without source metadata."""
    return (
        str(item.get("object_type") or "").casefold() == "workflow"
        or "workflow" in {str(value).casefold() for value in item.get("retrieval_channels", [])}
    )


def _requirement_evidence(
    requirements: list[dict[str, str]], evidence: dict[str, dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Give review/revision a compact, relevant evidence subset per requirement."""
    selected: dict[str, list[dict[str, Any]]] = {}
    for requirement in requirements:
        requirement_id = str(requirement["id"])
        if requirement_id == "factory_composition":
            matches = [
                item for item in evidence.values()
                if _contains_any(
                    _evidence_search_text(item),
                    ("factory", "setacceptance", "generate1dmodel", "generate2dmodel", "generate model"),
                )
            ]
        elif requirement_id == "divergence_factory_composition":
            matches = [
                item for item in evidence.values()
                if _contains_any(
                    _evidence_search_text(item),
                    ("factory", "divergence", "smearing", "generate2dmodel", "generate model"),
                )
            ]
        elif requirement_id == "acceptance_factory_application":
            matches = [
                item for item in evidence.values()
                if _contains_any(
                    _evidence_search_text(item),
                    ("factory", "acceptance", "setacceptance", "generate2dmodel", "generate model"),
                )
            ]
        elif requirement_id == "source_role_grounding":
            # F6-A2-FR2-R1: give revision the selected evidence of each source
            # kind the plan requires, so a substantively grounded claim can be
            # written for an uncovered kind (never a provenance-only mention).
            matches = [
                item
                for item in evidence.values()
                if _evidence_source_types(item) & set(requirement.get("required_source_types") or [])
            ]
        elif requirement_id == "elastic_cross_section_luminosity_fit":
            matches = [
                item for item in evidence.values()
                if _contains_any(
                    _evidence_search_text(item),
                    (
                        "elastic", "differential cross section", "differential cross-section",
                        "luminosity", "fit", "fitting", "measured distribution",
                    ),
                )
            ]
        elif requirement_id == "reader_selection_histogram_accounting":
            matches = [
                item for item in evidence.values()
                if "pndlmddatareader" in _evidence_search_text(item)
                or _contains_any(
                    _evidence_search_text(item),
                    ("selection", "filter", "accepted", "generated", "histogram"),
                )
            ]
        elif requirement_id == "pointer_identifier_normalization":
            pointer_target = str(requirement.get("target_symbol") or "").casefold()
            matches = [
                item for item in evidence.values()
                if (bool(pointer_target) and pointer_target in _evidence_search_text(item))
                or _contains_any(_evidence_search_text(item), ("pointer", "type expression"))
            ]
        elif requirement_id == "model_layer_component_inventory":
            matches = [
                item for item in evidence.values()
                if _contains_any(
                    _evidence_search_text(item),
                    ("dpm", "acceptance", "smearing", "resolution", "divergence", "modelfactory"),
                )
            ]
        elif requirement_id == "implementation_disambiguation_procedure":
            matches = [
                item for item in evidence.values()
                if (item.get("locator") or {}).get("path")
                and str(item.get("source_id") or "") in {
                    "luminosityfit", "pandaroot", "restgas_determination"
                }
            ]
        elif requirement_id == "efficiency_empty_bin_diagnosis":
            matches = [
                item for item in evidence.values()
                if _contains_any(
                    _evidence_search_text(item),
                    (
                        "numerator", "reconstructed", "selection", "migration", "denominator",
                        "zero efficiency", "empty bin", "binning", "profile", "compatibility",
                    ),
                )
            ]
        elif requirement_id == "workflow_or_operational_grounding":
            workflow_matches = [item for item in evidence.values() if _is_workflow_evidence(item)]
            documentation_matches = [
                item for item in evidence.values()
                if "sphinx" in str(item.get("source_id") or "").casefold()
                or bool((item.get("locator") or {}).get("url"))
            ]
            matches = workflow_matches or documentation_matches
        else:
            matches = []
        if matches:
            selected[requirement_id] = _compact_requirement_evidence(
                matches, requirement_id, str(requirement.get("target_symbol") or "")
            )
    return selected


def _compact_requirement_evidence(
    matches: list[dict[str, Any]], requirement_id: str, target_symbol: str = ""
) -> list[dict[str, Any]]:
    """Keep the model-facing requirement subset near the relevant factory code."""
    anchors = {
        "factory_composition": ("factory", "setacceptance", "generate2dmodel", "generate model"),
        "divergence_factory_composition": ("divergence", "smearing", "factory", "generate2dmodel"),
        "acceptance_factory_application": ("acceptance", "setacceptance", "factory", "generate2dmodel"),
        "elastic_cross_section_luminosity_fit": (
            "elastic", "differential cross section", "luminosity", "fit", "measured distribution",
        ),
        "reader_selection_histogram_accounting": (
            "pndlmddatareader", "selection", "filter", "accepted", "generated", "histogram",
        ),
        "model_layer_component_inventory": (
            "dpm", "acceptance", "smearing", "resolution", "divergence", "modelfactory",
        ),
        "implementation_disambiguation_procedure": (
            "source", "path", "implementation", "caller", "data product", "branch",
        ),
        "efficiency_empty_bin_diagnosis": (
            "numerator", "reconstructed", "migration", "denominator", "zero efficiency", "binning", "profile",
        ),
    }.get(requirement_id, ())
    if requirement_id == "pointer_identifier_normalization":
        anchors = (target_symbol.casefold(),) if target_symbol else ()
        anchors += ("pointer", "type expression")
    compact: list[dict[str, Any]] = []
    for item in matches[:4]:
        clone = dict(item)
        text = str(item.get("text") or "")
        lowered = text.casefold()
        positions = [lowered.find(anchor) for anchor in anchors if lowered.find(anchor) >= 0]
        if positions:
            start = max(0, min(positions) - 400)
            clone["text"] = text[start:start + 1800]
        compact.append(clone)
    return compact


def _deterministic_missing_requirement_ids(
    requirements: list[dict[str, str]], claims: list[dict[str, Any]], evidence: dict[str, dict[str, Any]]
) -> list[str]:
    """Backstop model review for high-value structural completeness checks."""
    claim_text = " ".join(str(claim.get("claim_text") or "") for claim in claims).casefold()
    cited_ids = {
        str(evidence_id)
        for claim in claims
        for evidence_id in claim.get("evidence_ids", [])
    }

    def cited_evidence_has(*term_groups: tuple[str, ...]) -> bool:
        cited_text = " ".join(
            _evidence_search_text(evidence[evidence_id])
            for evidence_id in cited_ids
            if evidence_id in evidence
        )
        return all(_contains_any(cited_text, terms) for terms in term_groups)

    missing: list[str] = []
    for requirement in requirements:
        requirement_id = str(requirement["id"])
        if requirement_id == "factory_composition":
            has_factory = "factory" in claim_text
            has_input_or_setter = any(term in claim_text for term in ("setacceptance", "setter", "configuration", "input"))
            has_construction = any(term in claim_text for term in ("generate1dmodel", "generate2dmodel", "generatemodel", "construct", "build"))
            if not (has_factory and has_input_or_setter and has_construction):
                missing.append(requirement_id)
        elif requirement_id == "divergence_factory_composition":
            has_divergence = any(term in claim_text for term in ("divergence", "smearing"))
            has_factory_path = "factory" in claim_text
            has_resulting_model = any(
                term in claim_text
                for term in ("fit model", "resulting model", "generated model", "construct", "compose", "convolut")
            )
            if not (has_divergence and has_factory_path and has_resulting_model):
                missing.append(requirement_id)
        elif requirement_id == "acceptance_factory_application":
            has_acceptance = "pndlmdacceptance" in claim_text
            has_storage = any(term in claim_text for term in ("setacceptance", "stored", "storage", "member"))
            has_construction = any(term in claim_text for term in ("generate1dmodel", "generate2dmodel", "generatemodel", "construct", "build"))
            has_application = any(term in claim_text for term in ("apply", "applied", "multiply", "multipl", "factor", "used by"))
            cited_handoff = cited_evidence_has(
                ("pndlmdacceptance",),
                ("setacceptance", "stored", "member"),
                ("generate1dmodel", "generate2dmodel", "generate model", "construct", "build"),
                ("apply", "applied", "multiply", "multipl", "factor", "used by"),
            )
            if not (has_acceptance and has_storage and has_construction and has_application and cited_handoff):
                missing.append(requirement_id)
        elif requirement_id == "source_role_grounding":
            # F6-A2-FR2-R1: the multi-source grounding requirement is satisfied
            # when the cited evidence covers every question-grounded source kind
            # the plan requires; an uncovered kind means the answer never
            # grounded any substantive part in that source.
            required_kinds = set(requirement.get("required_source_types") or [])
            if required_kinds:
                cited_types: set[str] = set()
                for evidence_id in cited_ids:
                    item = evidence.get(evidence_id)
                    if item is not None:
                        cited_types |= _evidence_source_types(item)
                if not required_kinds <= cited_types:
                    missing.append(requirement_id)
        elif requirement_id == "elastic_cross_section_luminosity_fit":
            has_cross_section = any(
                term in claim_text
                for term in ("elastic", "differential cross section", "differential cross-section")
            )
            has_theory_input = any(term in claim_text for term in ("theory", "model", "input"))
            has_measured_fit = any(
                term in claim_text for term in ("fit", "fitting", "measured distribution", "distribution")
            )
            has_luminosity = "luminosity" in claim_text
            cited_chain = cited_evidence_has(
                ("elastic", "differential cross section", "differential cross-section"),
                ("luminosity",),
                ("fit", "fitting", "measured distribution", "distribution"),
            )
            if not (has_cross_section and has_theory_input and has_measured_fit and has_luminosity and cited_chain):
                missing.append(requirement_id)
        elif requirement_id == "reader_selection_histogram_accounting":
            has_reader = "pndlmddatareader" in claim_text
            has_selection = any(term in claim_text for term in ("selection", "filter"))
            has_accounting = (
                any(term in claim_text for term in ("accepted", "acceptance"))
                and "generated" in claim_text
                and any(term in claim_text for term in ("histogram", "histograms", "fill", "filling"))
            )
            cited_accounting = cited_evidence_has(
                ("pndlmddatareader",),
                ("selection", "filter"),
                ("accepted", "acceptance"),
                ("generated",),
                ("histogram", "fill", "filling"),
            )
            if not (has_reader and has_selection and has_accounting and cited_accounting):
                missing.append(requirement_id)
        elif requirement_id == "pointer_identifier_normalization":
            pointer_target = str(requirement.get("target_symbol") or "").casefold()
            has_pointer_type = (
                bool(pointer_target)
                and (
                    f"{pointer_target}*" in claim_text
                    or (pointer_target in claim_text and "pointer" in claim_text)
                )
            )
            has_underlying_symbol = (
                bool(pointer_target)
                and "underlying" in claim_text
                and pointer_target in claim_text
            )
            has_qualifier_rule = (
                any(term in claim_text for term in ("asterisk", "pointer syntax", "type-expression syntax", "type expression syntax"))
                and any(term in claim_text for term in ("not part", "does not form", "not a new", "remove", "strip"))
            )
            if not (has_pointer_type and has_underlying_symbol and has_qualifier_rule):
                missing.append(requirement_id)
        elif requirement_id == "model_layer_component_inventory":
            has_physics = any(term in claim_text for term in ("dpm", "cross section", "physics model"))
            has_acceptance = "acceptance" in claim_text
            has_smearing = any(term in claim_text for term in ("resolution", "smearing", "divergence"))
            has_factory = "factory" in claim_text or "pndlmdmodelfactory" in claim_text
            if not (has_physics and has_acceptance and has_smearing and has_factory):
                missing.append(requirement_id)
        elif requirement_id == "implementation_disambiguation_procedure":
            has_name_warning = (
                "name" in claim_text
                and any(term in claim_text for term in ("insufficient", "not enough", "does not establish", "cannot establish"))
            )
            has_provenance = (
                any(term in claim_text for term in ("source_id", "source", "repository"))
                and "path" in claim_text
            )
            has_behavior_check = (
                "implementation" in claim_text
                and any(term in claim_text for term in ("caller", "configuration", "configured"))
                and any(term in claim_text for term in ("data product", "branch", "consumed", "produced"))
            )
            if not (has_name_warning and has_provenance and has_behavior_check):
                missing.append(requirement_id)
        elif requirement_id == "efficiency_empty_bin_diagnosis":
            has_numerator_cause = (
                "numerator" in claim_text
                and any(term in claim_text for term in ("reconstructed", "selection", "migration"))
            )
            has_denominator_handling = (
                "denominator" in claim_text
                and "zero" in claim_text
                and "efficiency" in claim_text
            )
            has_compatibility = "binning" in claim_text and any(
                term in claim_text for term in ("profile", "compatib", "range")
            )
            cited_diagnosis = cited_evidence_has(
                ("numerator",),
                ("reconstructed", "selection", "migration"),
                ("denominator",),
                ("zero",),
                ("efficiency",),
                ("binning",),
                ("profile", "compatibility", "range"),
            )
            if not (has_numerator_cause and has_denominator_handling and has_compatibility and cited_diagnosis):
                missing.append(requirement_id)
        elif requirement_id == "workflow_or_operational_grounding":
            requirement_items = _requirement_evidence([requirement], evidence).get(requirement_id, [])
            if requirement_items:
                workflow_items = [item for item in requirement_items if _is_workflow_evidence(item)]
                if workflow_items:
                    grounded = any(
                        _is_workflow_evidence(evidence[evidence_id])
                        for evidence_id in cited_ids
                        if evidence_id in evidence
                    )
                else:
                    grounded = any(
                        evidence_id in {str(item["evidence_id"]) for item in requirement_items}
                        for evidence_id in cited_ids
                    )
                if not grounded:
                    missing.append(requirement_id)
    return missing


def _claim_audit_record(claim: dict[str, Any], reason: str) -> dict[str, Any]:
    """Produce a compact, diagnostic-only record for a filtered claim."""
    return {
        "claim_id": str(claim.get("claim_id") or ""),
        "evidence_ids": list(claim.get("evidence_ids") or []),
        "answer_point_ids": list(claim.get("answer_point_ids") or []),
        "filter_reason": reason,
    }


def render_verified_answer(claims: list[ClaimCitation]) -> str:
    """Render a final answer exclusively from already verified claims."""
    return "\n".join(
        f"{claim.claim_text.strip()} [{', '.join(claim.evidence_ids)}]"
        for claim in claims
    )


_COMPOSER_CAUSAL_CUES = ("because", "therefore", "thus", "causes", "caused by", "leads to", "results in", "hence", "因此", "因为", "导致", "从而")
_COMPOSER_COMPARISON_CUES = ("unlike", "whereas", "compared with", "compared to", "higher", "lower", "more than", "less than", "different from", "相比", "不同", "更高", "更低")
_COMPOSER_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_:@./-]+")
_COMPOSER_INNER_CASE_TRANSITION = re.compile(r"[a-z][A-Z]|[A-Z][a-z]")
# Numeric literals carry an explicit sign only when it directly precedes the
# digits, and a lookbehind keeps digits embedded in technical identifiers
# (PndPidCorrelatorV2, sha256, v1.2) from becoming standalone literals (F5-R1).
_COMPOSER_NUMERIC_PATTERN = re.compile(r"(?<![\w.])[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?%?")


def _composer_technical_tokens(text: str) -> list[str]:
    """Conservatively extract code-like tokens whose spelling must be preserved.

    A candidate token is kept only when it is plausibly code or data: a scoped
    name, a path, a code/data file extension, a repo@version form, an
    underscore identifier, or a token with an inner case transition. Plain
    Capitalized and plain lowercase prose words are not technical tokens.
    """
    tokens: list[str] = []
    for candidate in _COMPOSER_TOKEN_PATTERN.findall(text):
        token = _normalise_rejected_identifier_token(candidate)
        if not token:
            continue
        is_technical = (
            "::" in token
            or "/" in token
            or token.endswith(_CODE_DATA_EXTENSIONS)
            or "@" in token
            or ("_" in token and len(token) >= 4)
            or bool(_COMPOSER_INNER_CASE_TRANSITION.search(token[1:]))
        )
        if is_technical and token not in tokens:
            tokens.append(token)
    return tokens


def _composer_numeric_literals(text: str) -> list[str]:
    """Extract exact numeric literals (no normalization) in first-seen order."""
    literals: list[str] = []
    for literal in _COMPOSER_NUMERIC_PATTERN.findall(text):
        if literal not in literals:
            literals.append(literal)
    return literals


def _validate_composed_paragraphs(paragraphs: Any, claims: list[ClaimCitation]) -> tuple[bool, list[str]]:
    """Run every deterministic composer guard and return (ok, error codes).

    Error codes: invalid_structure, empty_paragraph, unknown_claim_id,
    duplicate_claim_id, missing_claim_id (exact-once coverage), new_identifier,
    new_numeric_literal, new_causal_relation, new_comparison_relation.
    """
    codes: list[str] = []

    def _fail(code: str) -> None:
        if code not in codes:
            codes.append(code)

    if not isinstance(paragraphs, list) or not paragraphs:
        return False, ["invalid_structure"]
    claim_map = {claim.claim_id: claim for claim in claims}
    content_paragraphs: list[dict[str, Any]] = []
    for paragraph in paragraphs:
        if (
            not isinstance(paragraph, dict)
            or not isinstance(paragraph.get("text"), str)
            or not isinstance(paragraph.get("source_claim_ids"), list)
            or not paragraph["source_claim_ids"]
            or any(not isinstance(claim_id, str) or not claim_id for claim_id in paragraph["source_claim_ids"])
        ):
            _fail("invalid_structure")
            continue
        if not paragraph["text"].strip():
            _fail("empty_paragraph")
            continue
        content_paragraphs.append(paragraph)
    flattened_ids = [
        claim_id
        for paragraph in content_paragraphs
        for claim_id in paragraph["source_claim_ids"]
    ]
    if any(claim_id not in claim_map for claim_id in flattened_ids):
        _fail("unknown_claim_id")
    if len(flattened_ids) != len(set(flattened_ids)):
        _fail("duplicate_claim_id")
    if sorted(flattened_ids) != sorted(claim_map):
        _fail("missing_claim_id")
    for paragraph in content_paragraphs:
        source_ids = paragraph["source_claim_ids"]
        if any(claim_id not in claim_map for claim_id in source_ids):
            # Unknown ids already recorded; content checks need real claims.
            continue
        source_text = " ".join(claim_map[claim_id].claim_text for claim_id in source_ids)
        source_casefold = source_text.casefold()
        paragraph_text = paragraph["text"]
        # Exact extracted-token provenance (F5-R1): paragraph technical tokens
        # and numeric literals must each appear verbatim among the tokens
        # extracted from the referenced claims; substring membership against
        # source prose is not sufficient (e.g. -3 vs 3, PndPidCorrelatorV2 vs
        # PndPidCorrelator).
        source_tokens = set(_composer_technical_tokens(source_text))
        source_token_aliases = {token.casefold() for token in source_tokens}
        for token in _composer_technical_tokens(paragraph_text):
            if token not in source_tokens:
                _fail("new_identifier")
        for word in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", paragraph_text):
            # Casing-alteration sentinel: a word that case-insensitively aliases
            # a source technical token but differs in exact spelling no longer
            # looks technical and must not bypass exact preservation.
            if word.casefold() in source_token_aliases and word not in source_tokens:
                _fail("new_identifier")
        source_literals = set(_composer_numeric_literals(source_text))
        for literal in _composer_numeric_literals(paragraph_text):
            if literal not in source_literals:
                _fail("new_numeric_literal")
        if _contains_any(paragraph_text.casefold(), _COMPOSER_CAUSAL_CUES) and not _contains_any(
            source_casefold, _COMPOSER_CAUSAL_CUES
        ):
            _fail("new_causal_relation")
        if _contains_any(paragraph_text.casefold(), _COMPOSER_COMPARISON_CUES) and not _contains_any(
            source_casefold, _COMPOSER_COMPARISON_CUES
        ):
            _fail("new_comparison_relation")
    return not codes, codes


def _validate_composer_review(review: Any, paragraph_count: int, claim_ids: set[str]) -> bool:
    """Fail-closed acceptance check for the composer semantic review verdict."""
    if not isinstance(review, dict):
        return False
    if review.get("valid") is not True:
        return False
    unsupported = review.get("unsupported_paragraph_indexes")
    missing_or_distorted = review.get("missing_or_distorted_claim_ids")
    if not isinstance(unsupported, list) or unsupported:
        return False
    if not isinstance(missing_or_distorted, list) or missing_or_distorted:
        return False
    if any(
        not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < paragraph_count
        for index in unsupported
    ):
        return False
    if any(
        not isinstance(claim_id, str) or claim_id not in claim_ids
        for claim_id in missing_or_distorted
    ):
        return False
    return isinstance(review.get("reason"), str)


def render_composed_answer(paragraphs: list[dict], claims: list[ClaimCitation]) -> str:
    """Render an accepted composition with app-derived, deduplicated citations."""
    claim_map = {claim.claim_id: claim for claim in claims}
    lines: list[str] = []
    for paragraph in paragraphs:
        evidence_ids: list[str] = []
        for claim_id in paragraph["source_claim_ids"]:
            for evidence_id in claim_map[claim_id].evidence_ids:
                if evidence_id not in evidence_ids:
                    evidence_ids.append(evidence_id)
        lines.append(f"{paragraph['text'].strip()} [{', '.join(evidence_ids)}]")
    return "\n".join(lines)


_QA_TRACE_MAX_EVENTS = 16
_QA_TRACE_MAX_BYTES = 2_097_152
_QA_TRACE_STAGES = (
    ("EA_ADMISSION", 0), ("A0_OUTPUT", 0), ("V1_INPUT", 1), ("V1_OUTPUT", 1),
    ("EA_ADMISSION", 1), ("A1_INPUT", 1), ("A1_OUTPUT", 1), ("A1_POST_MERGE", 1),
    ("V2_INPUT", 2), ("V2_OUTPUT", 2), ("C_INPUT", 0), ("C_OUTPUT", 0),
)


def _trace_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


class _QAStageTrace:
    """Invocation-local, best-effort parsed-data capture; never semantic authority."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.registry: dict[str, Any] = {}
        self.incomplete = False
        self.failure_codes: list[str] = []

    def _envelope(self) -> dict[str, Any]:
        return {"schema_version": "qa-stage-trace-v1",
                "capture_status": "INCOMPLETE" if self.incomplete else "COMPLETE",
                "events": self.events, "evidence_registry": self.registry,
                "failure_codes": self.failure_codes}

    def _project(self, value: Any, registry: dict[str, Any]) -> Any:
        if isinstance(value, dict):
            if "evidence_id" in value and "text" in value:
                for key, old in registry.items():
                    if old == value:
                        return {"evidence_projection_ref": key}
                key = f"projection.{len(registry) + 1}"
                registry[key] = value
                return {"evidence_projection_ref": key}
            return {k: self._project(v, registry) for k, v in value.items()}
        if isinstance(value, list):
            return [self._project(v, registry) for v in value]
        return value

    def failure(self, stage: str, round_: int, code: str) -> None:
        self.incomplete = True
        if code not in self.failure_codes:
            self.failure_codes.append(code)
        item = {"stage": stage, "round": round_, "status": "NOT_CAPTURED",
                "reason_code": code, "payload": {}}
        for index, old in enumerate(self.events):
            if (old["stage"], old["round"]) == (stage, round_):
                self.events[index] = item
                return
        if len(self.events) < _QA_TRACE_MAX_EVENTS:
            self.events.append(item)

    def record(self, stage: str, round_: int, payload: Any, *, update: bool = False) -> None:
        # Serialization copies parsed data and rejects non-JSON objects before they
        # can escape into the existing evaluation store. Never retain live aliases.
        copied = json.loads(_trace_json(payload))
        registry = dict(self.registry)
        projected = self._project(copied, registry)
        index = next((i for i, e in enumerate(self.events)
                      if (e["stage"], e["round"]) == (stage, round_)), None)
        if index is None and len(self.events) >= _QA_TRACE_MAX_EVENTS:
            self.failure(stage, round_, "TRACE_EVENT_BOUND_EXCEEDED")
            return
        if update and index is not None:
            if self.events[index]["status"] == "NOT_CAPTURED":
                return
            projected = {**self.events[index]["payload"], **projected}
        event = {"stage": stage, "round": round_, "status": "CAPTURED",
                 "reason_code": None, "payload": projected}
        events = list(self.events)
        if index is None:
            events.append(event)
        else:
            events[index] = event
        envelope = {**self._envelope(), "events": events, "evidence_registry": registry}
        if len(_trace_json(envelope).encode("utf-8")) > _QA_TRACE_MAX_BYTES:
            self.failure(stage, round_, "TRACE_SIZE_BOUND_EXCEEDED")
            return
        self.events, self.registry = events, registry

    def finish(self) -> dict[str, Any]:
        for stage, round_ in _QA_TRACE_STAGES:
            if not any((e["stage"], e["round"]) == (stage, round_) for e in self.events):
                if len(self.events) >= _QA_TRACE_MAX_EVENTS:
                    self.incomplete = True
                    if "TRACE_EVENT_BOUND_EXCEEDED" not in self.failure_codes:
                        self.failure_codes.append("TRACE_EVENT_BOUND_EXCEEDED")
                    break
                reason = "NO_REVISION" if round_ in {1, 2} and stage not in {"V1_INPUT", "V1_OUTPUT"} else "STAGE_NOT_REACHED"
                self.events.append({"stage": stage, "round": round_, "status": "NOT_EXECUTED",
                                    "reason_code": reason, "payload": {}})
        result = self._envelope()
        if len(_trace_json(result).encode("utf-8")) > _QA_TRACE_MAX_BYTES:
            return _trace_incomplete("TRACE_SIZE_BOUND_EXCEEDED")
        return result


def _trace_incomplete(code: str) -> dict[str, Any]:
    return {"schema_version": "qa-stage-trace-v1", "capture_status": "INCOMPLETE",
            "reason_code": code, "events": [], "evidence_registry": {}}


def _trace(state: Any, stage: str, round_: int, payload: Callable[[], Any],
           *, update: bool = False) -> None:
    collector = state.get("_stage_trace")
    if collector is None:
        return
    try:
        collector.record(stage, round_, payload(), update=update)
    except Exception:
        try:
            collector.failure(stage, round_, "CAPTURE_FAILED")
        except Exception:
            # Optional telemetry cannot replace the original answer/exception.
            pass


def _trace_admission(state: Any, admitted: list[dict[str, Any]], round_: int) -> None:
    def payload() -> dict[str, Any]:
        selected = state["bundle"]["evidence"]
        admitted_ids = [e["evidence_id"] for e in admitted]
        payload = {"use": "A0" if round_ == 0 else "A1",
                "selected_evidence_ids": [e["evidence_id"] for e in selected],
                "admitted_evidence_ids": admitted_ids,
                "rejected_evidence_ids": [e["evidence_id"] for e in selected
                                          if e["evidence_id"] not in admitted_ids],
                "decisions": [{"evidence_id": e["evidence_id"],
                               "reason_code": "DIRECTLY_CITATION_ELIGIBLE" if e["evidence_id"] in admitted_ids
                               else "INCOMPLETE_SPHINX_LOCATOR",
                               "missing_locator_fields": [k for k in ("url", "snapshot_date", "section_path")
                                                          if not (e.get("locator") or {}).get(k)]
                               if e["evidence_id"] not in admitted_ids else []} for e in selected],
                "selected_evidence": selected, "untrusted_evidence": admitted}
        if state.get("_ea_cache", {}).get("decisions") is not None:
            payload["decisions"] = [
                {**original, **resolved}
                for original, resolved in zip(payload["decisions"], state["_ea_cache"]["decisions"])
            ]
        return payload
    _trace(state, "EA_ADMISSION", round_, payload)


def _trace_merge(state: Any, ordinal: int, old_id: str, new_id: str | None,
                 code: str, retained: bool, target: Callable[[], Any],
                 *, collection: str = "dispositions") -> None:
    def payload() -> dict[str, Any]:
        collector = state["_stage_trace"]
        old = next((e["payload"].get(collection, []) for e in collector.events
                    if e["stage"] == "A1_POST_MERGE"), [])
        return {collection: [*old, {"input_ordinal": ordinal,
                "old_claim_id": old_id, "new_claim_id": new_id,
                "disposition": code, "retained": retained, "comparison_target": target()}]}
    _trace(state, "A1_POST_MERGE", 1, payload, update=True)


class QAState(TypedDict, total=False):
    revisionable_relationships: list[dict[str, Any]]
    revisionable_unsupported_claim_ids: list[str]
    revisionable_unsupported_claim_mappings: dict[str, list[str]]
    coverage_blocked: bool
    coverage_satisfaction_status: str
    _stage_trace: Any
    _ea_cache: dict[str, Any]
    question: str
    answer_point_coverage_mode: str
    runtime_answer_points: list[dict[str, str]]
    missing_answer_point_ids: list[str]
    answer_point_audit: dict[str, Any]
    bundle: dict[str, Any]
    sufficient: bool
    draft: dict[str, Any]
    errors: list[str]
    supported_claims: list[dict[str, Any]]
    unsupported_claim_ids: list[str]
    missing_requirement_ids: list[str]
    answer_requirements: list[dict[str, str]]
    claim_audit: list[dict[str, Any]]
    revision_count: int
    retrieval_count: int
    missing_point_retrieval_count: int
    original_plan: dict[str, Any]
    candidate_snapshots: list[dict[str, Any]]
    retained_supported_claims: list[dict[str, Any]]
    retained_support_evidence: dict[str, dict[str, Any]]
    e3_trace: dict[str, Any]
    node_timings_ms: dict[str, int]
    composer_diagnostics: dict[str, Any]
    result: dict[str, Any]


def _build_missing_point_retrieval_objective(
    question: str,
    missing_point_ids: list[str],
    runtime_answer_points: list[dict[str, Any]],
) -> str:
    missing_id_set = set(missing_point_ids)
    missing_points = [
        p for p in runtime_answer_points
        if p.get("answer_point_id") in missing_id_set
    ]
    lines = [question.strip(), "", "Target missing question aspects:"]
    for p in missing_points:
        text = p.get("text", "").strip()
        if text:
            lines.append(f"- {text}")
    return "\n".join(lines)


def _claim_matches_retained(claim: dict[str, Any], retained: dict[str, Any]) -> bool:
    if claim.get("claim_id") != retained.get("claim_id"):
        return False
    if claim.get("claim_text") != retained.get("claim_text"):
        return False
    if list(claim.get("evidence_ids") or []) != list(retained.get("evidence_ids") or []):
        return False
    if list(claim.get("answer_point_ids") or []) != list(retained.get("answer_point_ids") or []):
        return False
    if "declared_answer_point_ids" in retained:
        if list(claim.get("declared_answer_point_ids", claim.get("answer_point_ids", []))) != list(retained.get("declared_answer_point_ids", [])):
            return False
    return True


class QAAgent:
    def __init__(
        self,
        project_root: Path,
        retriever: Retriever | None = None,
        vertex: VertexAIClient | None = None,
        verification_vertex: VertexAIClient | None = None,
    ) -> None:
        self.project_root = project_root
        if vertex is None:
            settings = VertexSettings.from_env()
            self.generation_vertex = VertexAIClient(settings)
            # F4: production default builds a DISTINCT verification client path
            # even when the effective verification model equals the generation
            # model.
            self.verification_vertex = VertexAIClient(settings.for_verification_model())
        else:
            # Legacy test/injection compatibility: a sole ``vertex=`` injection
            # serves both roles until a ``verification_vertex=`` is supplied
            # explicitly.
            self.generation_vertex = vertex
            self.verification_vertex = verification_vertex or vertex
        self.vertex = self.generation_vertex  # legacy alias
        self.retriever = retriever or Retriever(project_root, vertex=self.generation_vertex)
        self._locked_identifier_symbols: dict[str, set[str]] | None = None
        graph = StateGraph(QAState)
        for name, node in (
            ("retrieve", self._retrieve),
            ("sufficiency", self._sufficiency),
            ("targeted_retrieve", self._targeted_retrieve),
            ("answer", self._answer),
            ("verify", self._verify),
            ("missing_point_retrieve", self._missing_point_retrieve),
            ("revise", self._revise),
            ("finalize", self._finalize),
        ):
            graph.add_node(name, self._timed_node(name, node))
        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "sufficiency")
        graph.add_conditional_edges(
            "sufficiency",
            lambda state: "answer" if state["sufficient"] else (
                "targeted" if state.get("retrieval_count", 0) < getattr(getattr(self.retriever, "policies", None), "max_targeted_retrievals", 1) and not state["bundle"]["plan"].get("version_conflicts") else "finalize"
            ),
            {"answer": "answer", "targeted": "targeted_retrieve", "finalize": "finalize"},
        )
        graph.add_edge("targeted_retrieve", "sufficiency")
        graph.add_edge("answer", "verify")
        graph.add_conditional_edges(
            "verify",
            self._after_verify_route,
            {"missing_point_retrieve": "missing_point_retrieve", "revise": "revise", "finalize": "finalize"},
        )
        graph.add_edge("missing_point_retrieve", "revise")
        graph.add_edge("revise", "verify")
        graph.add_edge("finalize", END)
        self.graph = graph.compile()

    def decompose_question(self, question: str) -> dict[str, Any]:
        """Explicit shadow diagnostic; never invoked by the production graph."""
        return QuestionDecomposer(self.generation_vertex).decompose(question)

    def _retrieve(self, state: QAState) -> dict[str, Any]:
        is_runtime = state.get("answer_point_coverage_mode") == "runtime_e1_v2"
        if not is_runtime:
            return {
                "bundle": self.retriever.retrieve(state["question"]),
                "revision_count": 0,
                "retrieval_count": 0,
            }
        bundle = self.retriever.retrieve(state["question"], capture_candidates=True)
        snapshots = []
        if "candidate_snapshot" in bundle:
            snapshots.append(bundle["candidate_snapshot"])
        return {
            "bundle": bundle,
            "original_plan": deepcopy(bundle.get("plan", {})),
            "candidate_snapshots": snapshots,
            "revision_count": 0,
            "retrieval_count": 0,
            "missing_point_retrieval_count": 0,
        }

    def _targeted_retrieve(self, state: QAState) -> dict[str, Any]:
        required = ", ".join(state["bundle"]["plan"]["required_source_types"])
        missing = ", ".join(state.get("errors", []))
        plan = RetrievalPlan.model_validate(state["bundle"]["plan"])
        missing_symbols = [
            error.split("symbol:", 1)[1]
            for error in state.get("errors", [])
            if "symbol:" in error
        ]
        plan.symbols = list(dict.fromkeys([*missing_symbols, *plan.symbols]))
        is_runtime = state.get("answer_point_coverage_mode") == "runtime_e1_v2"
        current_retrieval_count = state.get("retrieval_count", 0) + 1
        query = state["question"] + f"\nTarget missing evidence sources: {required}. Missing evidence details: {missing}"
        if is_runtime:
            extra = self.retriever.retrieve(query, plan=plan, capture_candidates=True)
        else:
            extra = self.retriever.retrieve(query, plan=plan)
        merged = {item["evidence_id"]: item for item in [*extra["evidence"], *state["bundle"]["evidence"]]}
        update: dict[str, Any] = {
            "bundle": {**state["bundle"], "evidence": list(merged.values())[:12]},
            "retrieval_count": current_retrieval_count,
        }
        if is_runtime:
            snapshots = list(state.get("candidate_snapshots", []))
            if "candidate_snapshot" in extra:
                snap = dict(extra["candidate_snapshot"])
                snap["pass_origin"] = f"pre_answer_targeted_{current_retrieval_count}"
                snapshots.append(snap)
            update["candidate_snapshots"] = snapshots
        return update

    def _check_e3_trigger(
        self,
        state: QAState,
        missing_answer_point_ids: list[str] | None = None,
        audit: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        if state.get("answer_point_coverage_mode") != "runtime_e1_v2":
            return False, "mode_not_runtime_e1_v2"
        if state.get("revision_count", 0) != 0:
            return False, "revision_count_not_zero"
        if state.get("missing_point_retrieval_count", 0) != 0:
            return False, "missing_point_retrieval_count_not_zero"

        plan = state.get("bundle", {}).get("plan", {})
        if plan.get("version_conflicts"):
            return False, "version_conflicts"

        if audit is None:
            audit = state.get("answer_point_audit") or {}
        if audit.get("review_error"):
            return False, "coverage_review_structural_error"
        if audit.get("coverage_evaluable") is not True:
            return False, "coverage_not_evaluable"

        missing_ids = missing_answer_point_ids if missing_answer_point_ids is not None else state.get("missing_answer_point_ids")
        if not missing_ids:
            return False, "no_missing_answer_points"

        runtime_points = state.get("runtime_answer_points") or []
        known_point_ids = {
            p["answer_point_id"]
            for p in runtime_points
            if isinstance(p, dict) and "answer_point_id" in p
        }
        if not set(missing_ids).issubset(known_point_ids):
            return False, "unknown_answer_point_id"

        return True, "genuine_missing_point"

    def _is_e3_trigger_eligible(self, state: QAState) -> bool:
        eligible, _ = self._check_e3_trigger(state)
        return eligible

    def _after_verify_route(self, state: QAState) -> str:
        if _coverage_satisfaction_enabled(state):
            repairable = state.get("revisionable_relationships") or state.get("revisionable_unsupported_claim_ids")
            return "revise" if repairable and state.get("revision_count", 0) < 1 else "finalize"
        if self._is_e3_trigger_eligible(state):
            return "missing_point_retrieve"
        if state.get("errors") and state.get("revision_count", 0) < 1:
            return "revise"
        return "finalize"

    def _missing_point_retrieve(self, state: QAState) -> dict[str, Any]:
        missing_point_retrieval_count = state.get("missing_point_retrieval_count", 0) + 1
        state["missing_point_retrieval_count"] = missing_point_retrieval_count

        supported_claims = list(state.get("supported_claims", []))
        retained_supported_claims = [
            {
                "claim_id": str(c.get("claim_id", "")),
                "claim_text": str(c.get("claim_text", "")),
                "evidence_ids": list(c.get("evidence_ids", [])),
                "answer_point_ids": list(c.get("answer_point_ids", [])),
                "declared_answer_point_ids": list(c.get("declared_answer_point_ids", c.get("answer_point_ids", []))),
            }
            for c in supported_claims
        ]

        prior_evidence = list(state.get("bundle", {}).get("evidence", []))
        prior_evidence_lookup = {item["evidence_id"]: deepcopy(item) for item in prior_evidence if "evidence_id" in item}
        cited_support_ids = {eid for c in retained_supported_claims for eid in c.get("evidence_ids", [])}
        retained_support_evidence = {
            eid: prior_evidence_lookup[eid]
            for eid in cited_support_ids
            if eid in prior_evidence_lookup
        }

        question = str(state.get("question", ""))
        missing_ids = list(state.get("missing_answer_point_ids", []))
        runtime_points = list(state.get("runtime_answer_points", []))
        retrieval_objective = _build_missing_point_retrieval_objective(question, missing_ids, runtime_points)
        final_limit = getattr(getattr(self.retriever, "policies", None), "final_evidence_limit", 12)
        pass_snapshots = list(state.get("candidate_snapshots", []))

        try:
            if not pass_snapshots:
                raise RuntimeError("missing candidate snapshot from initial pass")

            original_plan_dict = state.get("original_plan") or state.get("bundle", {}).get("plan", {})
            frozen_plan = RetrievalPlan.model_validate(deepcopy(original_plan_dict))

            if not hasattr(self.retriever, "collect_channel_candidates"):
                raise RuntimeError("retriever lacks collect_channel_candidates capability")

            targeted_result = self.retriever.collect_channel_candidates(retrieval_objective, frozen_plan)
            if isinstance(targeted_result, dict) and "rankings" in targeted_result:
                targeted_rankings = targeted_result["rankings"]
                targeted_supplemental = list(targeted_result.get("supplemental_candidates") or [])
            else:
                targeted_rankings = targeted_result or {}
                targeted_supplemental = []

            targeted_snapshot = {
                "pass_origin": "e3_targeted",
                "rankings": targeted_rankings,
                "supplemental_candidates": targeted_supplemental,
            }

            all_snapshots = [*pass_snapshots, targeted_snapshot]

            has_targeted = any(bool(items) for items in targeted_rankings.values()) or bool(targeted_supplemental)
            if not has_targeted:
                # Empty targeted candidates must stop E3 rerank/update even if old unselected candidates could now enter
                e3_trace = {
                    "triggered": True,
                    "trigger_reason": "genuine_missing_point",
                    "missing_answer_point_ids": missing_ids,
                    "missing_answer_points": [
                        p for p in runtime_points if p.get("answer_point_id") in set(missing_ids)
                    ],
                    "retrieval_objective": retrieval_objective,
                    "missing_point_retrieval_count": missing_point_retrieval_count,
                    "pre_answer_retrieval_count": state.get("retrieval_count", 0),
                    "initial_selected_evidence_ids": [item.get("evidence_id") for item in prior_evidence],
                    "candidate_pass_provenance": [
                        {"pass_origin": s.get("pass_origin"), "channels": list(s.get("rankings", {}).keys())}
                        for s in all_snapshots
                    ],
                    "targeted_candidate_object_ids": [],
                    "dedup_result": {
                        "total_unique_objects": len(prior_evidence),
                        "consistency_failures": [],
                    },
                    "pass_occurrences": {},
                    "global_fused_candidate_object_ids": [],
                    "globally_selected_evidence_ids": [item.get("evidence_id") for item in prior_evidence],
                    "global_selected_object_ids": [item.get("object_id") for item in prior_evidence],
                    "newly_admitted_object_ids": [],
                    "displaced_selected_evidence_ids": [],
                    "retained_support_evidence_ids": list(retained_support_evidence.keys()),
                    "retained_supported_claims": retained_supported_claims,
                    "selected_evidence_count": len(prior_evidence),
                    "selected_evidence_budget": final_limit,
                    "retained_support_context_count": len(retained_support_evidence),
                    "atomic_update_status": "no_gain",
                    "no_gain": True,
                    "failure_reason": "empty_targeted_candidates",
                    "post_retrieval_missing_point_result": None,
                    "post_retrieval_coverage_evaluable": None,
                    "recovered_answer_point_ids": [],
                    "remaining_missing_answer_point_ids": missing_ids,
                }
                return {
                    "bundle": dict(state.get("bundle", {})),
                    "missing_point_retrieval_count": missing_point_retrieval_count,
                    "retained_supported_claims": retained_supported_claims,
                    "retained_support_evidence": retained_support_evidence,
                    "e3_trace": e3_trace,
                }

            if not hasattr(self.retriever, "consolidate_and_select_candidates"):
                raise RuntimeError("retriever lacks consolidate_and_select_candidates capability")

            consolidation = self.retriever.consolidate_and_select_candidates(
                original_question=question,
                plan=frozen_plan,
                pass_snapshots=all_snapshots,
                current_selected_evidence=prior_evidence,
            )

            status = consolidation.get("status", "no_gain")
            failure_reason = consolidation.get("failure_reason")
            newly_admitted_ids = consolidation.get("newly_admitted_object_ids", [])
            displaced_ids = consolidation.get("displaced_evidence_ids", [])
            fused_candidate_ids = consolidation.get("fused_candidate_ids", [])
            targeted_candidate_object_ids = list(dict.fromkeys([
                item["object_id"]
                for items in targeted_rankings.values()
                for item in items
                if "object_id" in item
            ] + [
                item["object_id"]
                for item in targeted_supplemental
                if "object_id" in item
            ]))

            bundle = dict(state.get("bundle", {}))
            if status == "success" and consolidation.get("selected_evidence"):
                bundle["evidence"] = consolidation["selected_evidence"]
                atomic_status = "success"
            else:
                atomic_status = status

            selected_evidence_ids = [item.get("evidence_id") for item in bundle.get("evidence", [])]
            selected_object_ids = [item.get("object_id") for item in bundle.get("evidence", [])]

            e3_trace = {
                "triggered": True,
                "trigger_reason": "genuine_missing_point",
                "missing_answer_point_ids": missing_ids,
                "missing_answer_points": [
                    p for p in runtime_points if p.get("answer_point_id") in set(missing_ids)
                ],
                "retrieval_objective": retrieval_objective,
                "missing_point_retrieval_count": missing_point_retrieval_count,
                "pre_answer_retrieval_count": state.get("retrieval_count", 0),
                "initial_selected_evidence_ids": [item.get("evidence_id") for item in prior_evidence],
                "candidate_pass_provenance": [
                    {"pass_origin": s.get("pass_origin"), "channels": list(s.get("rankings", {}).keys())}
                    for s in all_snapshots
                ],
                "targeted_candidate_object_ids": targeted_candidate_object_ids,
                "dedup_result": {
                    "total_unique_objects": len(consolidation.get("payloads", consolidation.get("best_channel_ranks", {}))),
                    "consistency_failures": consolidation.get("consistency_failures", []),
                },
                "pass_occurrences": consolidation.get("pass_occurrences", {}),
                "global_fused_candidate_object_ids": fused_candidate_ids,
                "globally_selected_evidence_ids": selected_evidence_ids,
                "global_selected_object_ids": selected_object_ids,
                "newly_admitted_object_ids": newly_admitted_ids,
                "displaced_selected_evidence_ids": displaced_ids,
                "retained_support_evidence_ids": list(retained_support_evidence.keys()),
                "retained_supported_claims": retained_supported_claims,
                "selected_evidence_count": len(selected_evidence_ids),
                "selected_evidence_budget": final_limit,
                "retained_support_context_count": len(retained_support_evidence),
                "atomic_update_status": atomic_status,
                "no_gain": atomic_status == "no_gain",
                "failure_reason": failure_reason,
                "post_retrieval_missing_point_result": None,
                "post_retrieval_coverage_evaluable": None,
                "recovered_answer_point_ids": [],
                "remaining_missing_answer_point_ids": missing_ids,
            }

            return {
                "bundle": bundle,
                "missing_point_retrieval_count": missing_point_retrieval_count,
                "retained_supported_claims": retained_supported_claims,
                "retained_support_evidence": retained_support_evidence,
                "e3_trace": e3_trace,
            }

        except Exception as exc:
            # Catch ordinary collection/fusion/rerank/selection failure once
            # Retain prior bundle and support, return trace failure and count=1
            e3_trace = {
                "triggered": True,
                "trigger_reason": "genuine_missing_point",
                "missing_answer_point_ids": missing_ids,
                "missing_answer_points": [
                    p for p in runtime_points if p.get("answer_point_id") in set(missing_ids)
                ],
                "retrieval_objective": retrieval_objective,
                "missing_point_retrieval_count": missing_point_retrieval_count,
                "pre_answer_retrieval_count": state.get("retrieval_count", 0),
                "initial_selected_evidence_ids": [item.get("evidence_id") for item in prior_evidence],
                "candidate_pass_provenance": [],
                "targeted_candidate_object_ids": [],
                "dedup_result": {
                    "total_unique_objects": 0,
                    "consistency_failures": [],
                },
                "pass_occurrences": {},
                "global_fused_candidate_object_ids": [],
                "globally_selected_evidence_ids": [item.get("evidence_id") for item in prior_evidence],
                "global_selected_object_ids": [item.get("object_id") for item in prior_evidence],
                "newly_admitted_object_ids": [],
                "displaced_selected_evidence_ids": [],
                "retained_support_evidence_ids": list(retained_support_evidence.keys()),
                "retained_supported_claims": retained_supported_claims,
                "selected_evidence_count": len(prior_evidence),
                "selected_evidence_budget": final_limit,
                "retained_support_context_count": len(retained_support_evidence),
                "atomic_update_status": "failure",
                "no_gain": True,
                "failure_reason": str(exc),
                "post_retrieval_missing_point_result": None,
                "post_retrieval_coverage_evaluable": None,
                "recovered_answer_point_ids": [],
                "remaining_missing_answer_point_ids": missing_ids,
            }
            return {
                "bundle": dict(state.get("bundle", {})),
                "missing_point_retrieval_count": missing_point_retrieval_count,
                "retained_supported_claims": retained_supported_claims,
                "retained_support_evidence": retained_support_evidence,
                "e3_trace": e3_trace,
            }

    def _locked_symbols(self) -> dict[str, set[str]]:
        """Load the restored database identifier catalog once per Agent."""
        if self._locked_identifier_symbols is None:
            symbols: set[str] = set()
            paths: set[str] = set()
            try:
                with self.retriever.storage.connect() as connection:
                    rows = connection.execute(
                        "SELECT locator,text FROM knowledge_objects"
                    ).fetchall()
            except Exception as exc:
                raise RuntimeError(
                    "locked identifier catalog database is unavailable"
                ) from exc
            for locator, text in rows:
                locator = locator or {}
                symbol = str(locator.get("symbol") or "")
                if symbol:
                    symbols.add(symbol)
                path = str(locator.get("path") or "").replace("\\", "/")
                if path:
                    paths.add(path)
                for match in re.finditer(
                    r"\b(?:class|struct|enum)\s+([A-Za-z_][A-Za-z0-9_]*)",
                    str(text or ""),
                ):
                    symbols.add(match.group(1))
            self._locked_identifier_symbols = {"symbols": symbols, "paths": paths}
        return self._locked_identifier_symbols

    def _answerability_guard(self, state: QAState) -> list[str]:
        """Reject requests whose requested result cannot exist in the corpus.

        A refusal can still carry a small, cited amount of verifiable schema or
        interface information.  The guard only controls the structured status;
        it never promotes that partial help to ``answered``.
        """
        question = str(state.get("question", ""))
        question_lower = question.casefold()
        plan = state["bundle"].get("plan", {})
        evidence = list(state["bundle"].get("evidence", []))
        exact_future_runtime_request = (
            _contains_any(question_lower, _FUTURE_RUNTIME_TERMS)
            and _contains_any(question_lower, _EXACT_RESULT_TERMS)
            and _contains_any(question_lower, _RUNTIME_ARTIFACT_TERMS)
        )
        if exact_future_runtime_request:
            return [
                "exact future runtime outcome or checksum cannot be established before execution"
            ]
        universal_proof_request = _contains_any(question_lower, _UNIVERSAL_PROOF_TERMS) and (
            _contains_any(question_lower, ("prove", "proof", "theorem", "证明", "定理"))
            and _contains_any(question_lower, ("for all", "every", "any", "universal", "所有", "任意", "普遍"))
        )
        if universal_proof_request and not _has_same_domain_formal_proof(question, evidence):
            return [
                "open-domain universal proof is unsupported without explicit same-domain theorem/proof evidence"
            ]
        catalog = self._locked_symbols()
        planned_symbols = [str(value) for value in plan.get("symbols", [])]
        requested_api = [
            value
            for value in planned_symbols
            if "::" in value
        ]
        requested_api.extend(
            re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*::[A-Za-z_][A-Za-z0-9_]*\b", question)
        )
        for raw in dict.fromkeys(requested_api):
            method = raw.rsplit("::", 1)[-1]
            if method not in catalog["symbols"] and raw not in catalog["symbols"]:
                return [f"unsupported requested API symbol: {raw}"]
        # Generic bare-class premise guard: the question itself must request or
        # assume the symbol, and the locked-corpus catalog — not the currently
        # selected evidence — decides whether it exists (F2-A4).
        # A manifest repository reference named in the question ("PandaRoot",
        # "LuminosityFit") is retrieval scope, not a code symbol: the locked
        # object catalog decides code symbols, the repository manifest decides
        # repository identities (F6-A-FR1).
        for raw in _requested_bare_class_symbols(question):
            if raw in catalog["symbols"] or raw in catalog["paths"]:
                continue
            if self.retriever.is_repository_reference(raw):
                continue
            return [f"unsupported requested symbol: {raw}"]
        deleted_artifact_request = (
            any(term in question_lower for term in ("deleted", "removed", "丢失", "删除"))
            and any(term in question_lower for term in ("recover", "reconstruct", "restore", "恢复", "重建"))
            and any(term in question_lower for term in ("source code", "from source", "源码", "event_poca", ".root", "runtime"))
        )
        if deleted_artifact_request:
            return ["runtime artifact records cannot be reconstructed from source code alone"]
        return []

    def _sufficiency(self, state: QAState) -> dict[str, Any]:
        evidence = state["bundle"]["evidence"]
        conflicts = state["bundle"]["plan"].get("version_conflicts", [])
        if conflicts:
            return {"sufficient": False, "errors": conflicts}
        guarded = self._answerability_guard(state)
        if guarded:
            return {"sufficient": False, "errors": guarded}
        question_lower = str(state.get("question", "")).casefold()
        evidence_text = " ".join(
            [
                item.get("text", "")
                + " "
                + str((item.get("locator") or {}).get("path") or "")
                for item in evidence
            ]
        ).casefold()
        # An exact resource requirement must be established by the corpus. A
        # generic CUDA or installation paragraph is not evidence of a minimum
        # GPU-memory value, so answer conservatively when that pairing is absent.
        exact_memory_question = (
            ("exact" in question_lower or "minimum" in question_lower)
            and any(term in question_lower for term in ("gpu", "memory", "ram"))
        )
        memory_requirement_supported = bool(
            re.search(
                r"(?:gpu|cuda).{0,60}(?:memory|ram)|(?:memory|ram).{0,60}(?:minimum|required|requirement)",
                evidence_text,
            )
        )
        if exact_memory_question and not memory_requirement_supported:
            return {
                "sufficient": False,
                "errors": ["evidence does not establish an exact GPU-memory requirement"],
            }
        source_types = set()
        for item in evidence:
            source_types |= _evidence_source_types(item)
        missing = [value for value in state["bundle"]["plan"]["required_source_types"] if value not in source_types]
        return {
            "sufficient": bool(evidence) and not missing,
            "errors": [f"missing required source: {value}" for value in missing] if evidence else ["no evidence"],
        }

    @staticmethod
    def _augment_planned_locators(draft: dict[str, Any], state: QAState) -> dict[str, Any]:
        """Add a minimal locator claim when an exact planned symbol was retrieved
        but the generation model omitted it from an otherwise valid answer.

        This is intentionally narrow: it only uses symbols already present in
        the deterministic retrieval plan and only adds a claim when a selected
        evidence item contains the same path/name.  It never invents a path or
        fetches new evidence.
        """
        question = str(state.get("question", ""))
        question_lower = question.casefold()
        locator_terms = (
            "where", "which code", "which file", "path", "located", "defined",
            "implementation", "哪里", "路径", "定义", "哪个文件", "实现",
        )
        if not any(term in question_lower for term in locator_terms):
            return draft
        claims = list(draft.get("claims", []))
        answer_text = " ".join(str(item.get("claim_text", "")) for item in claims)
        evidence = state["bundle"].get("evidence", [])
        additions = 0
        for raw_symbol in state["bundle"]["plan"].get("symbols", []):
            raw = str(raw_symbol).replace("\\", "/")
            if raw.lower().endswith((".md", ".html")) or "/readme" in raw.lower():
                continue
            basename = raw.rsplit("/", 1)[-1]
            stem = basename.rsplit(".", 1)[0] if "." in basename else basename
            names = [value for value in (raw, basename, stem) if value]
            if not any(value.casefold() in question_lower for value in names):
                continue
            if any(value.casefold() in answer_text.casefold() for value in names):
                continue
            matches = []
            for item in evidence:
                locator = item.get("locator") or {}
                locator_text = " ".join(
                    str(locator.get(key) or "")
                    for key in ("path", "symbol", "url")
                )
                haystack = f"{locator_text} {item.get('text', '')}"
                if any(value in haystack for value in names):
                    matches.append(item)
            if not matches:
                continue
            # Preserve extensions for ROOT macros and correction scripts; for
            # C++ source files the class/function stem is the useful identifier.
            display = basename if basename.endswith(".C") else stem
            claim_id = "locator_" + "_".join(ch for ch in display if ch.isalnum() or ch == "_")
            if any(claim.get("claim_id") == claim_id for claim in claims):
                continue
            claims.append(
                {
                    "claim_id": claim_id,
                    "claim_text": f"The relevant implementation locator is {display} at {raw}.",
                    "evidence_ids": [item["evidence_id"] for item in matches[:2]],
                    "answer_point_ids": [] if _coverage_shadow(state) else [RUNTIME_ANSWER_POINT_ID],
                    **({"_unresolved_locator_mapping": True} if _coverage_shadow(state) else {}),
                }
            )
            additions += 1
            if additions >= 1:
                break
        draft["claims"] = claims
        return draft

    @staticmethod
    def _augment_required_dataflow_evidence(
        draft: dict[str, Any], state: QAState
    ) -> dict[str, Any]:
        """Keep data-flow answers from dropping required code/workflow hand-offs.

        The generator may correctly explain the theory while citing only the
        paper, even though retrieval supplied exact implementation evidence.
        For data-flow questions, add narrow locator claims for supplied plan
        symbols and one supplied workflow/code item per required source type.
        This never invents a locator or fetches new evidence.

        E1/E2 coverage modes own completeness through claim-to-answer-point
        coverage, so plan-suggested source types and symbols must not synthesize
        additional claims there; this augmentation stays a legacy-default
        bridge.
        """
        if _coverage_shadow(state):
            return draft
        plan = state.get("bundle", {}).get("plan", {})
        if plan.get("intent") != "data_flow":
            return draft
        required_sources = set(plan.get("required_source_types", []))
        evidence = list(state.get("bundle", {}).get("evidence", []))
        claims = list(draft.get("claims", []))
        cited_ids = {
            evidence_id
            for claim in claims
            for evidence_id in claim.get("evidence_ids", [])
        }

        def source_type(item: dict[str, Any]) -> str:
            source_id = str(item.get("source_id") or "")
            object_type = str(item.get("object_type") or "")
            path = str((item.get("locator") or {}).get("path") or "").replace("\\", "/")
            channels = set(item.get("retrieval_channels", []))
            if source_id in {"li_2026", "karavdina_2015", "pflueger_2017"}:
                return "paper"
            if object_type in {"workflow", "python_script", "shell_script"} or channels & {"workflow", "graph"}:
                return "workflow"
            if path.lower().startswith(("docs/", "doc/")):
                return "documentation"
            return "code"

        for required in sorted(required_sources & {"code", "workflow"}):
            if any(source_type(item) == required and item.get("evidence_id") in cited_ids for item in evidence):
                continue
            match = next((item for item in evidence if source_type(item) == required), None)
            if not match:
                continue
            evidence_id = str(match.get("evidence_id"))
            locator = match.get("locator") or {}
            location = locator.get("path") or locator.get("symbol") or match.get("source_id")
            claim_id = f"required_{required}"
            if any(claim.get("claim_id") == claim_id for claim in claims):
                continue
            claims.append(
                {
                    "claim_id": claim_id,
                    "claim_text": f"The {required} evidence identifies {location} as part of the requested data flow.",
                    "evidence_ids": [evidence_id],
                }
            )
            cited_ids.add(evidence_id)

        symbols = [str(value).replace("\\", "/") for value in plan.get("symbols", [])]
        for raw in symbols:
            if raw.lower().endswith((".html", ".md")):
                continue
            basename = raw.rsplit("/", 1)[-1]
            stem = basename.rsplit(".", 1)[0] if "." in basename else basename
            if any(stem.casefold() in str(claim.get("claim_text", "")).casefold() for claim in claims):
                continue
            match = next(
                (
                    item
                    for item in evidence
                    if stem.casefold()
                    in " ".join(
                        str((item.get("locator") or {}).get(key) or "")
                        for key in ("path", "symbol", "url")
                    ).casefold()
                ),
                None,
            )
            if not match:
                continue
            display = basename if basename.endswith(".C") else stem
            claims.append(
                {
                    "claim_id": "dataflow_locator_" + "_".join(
                        char for char in display if char.isalnum() or char == "_"
                    ),
                    "claim_text": f"The data-flow implementation includes {display} at {raw}.",
                    "evidence_ids": [str(match.get("evidence_id"))],
                }
            )
        draft["claims"] = claims
        return draft

    def _admitted_evidence(self, state: QAState) -> list[dict[str, Any]]:
        """Resolve real citation backing once, without altering retrieval evidence."""
        selected = state["bundle"]["evidence"]
        # E3 changes its treatment bundle after A0; preserve that experimental
        # contract rather than reusing a pre-treatment EA cache or resolving its ledger.
        if state.get("answer_point_coverage_mode") == "runtime_e1_v2":
            return [e for e in selected if _is_public_claim_citation_eligible(e)]
        cache = state.setdefault("_ea_cache", {})
        if "projection" in cache:
            return cache["projection"]
        direct = [e for e in selected if _is_public_claim_citation_eligible(e)]
        decisions = [{"evidence_id": e["evidence_id"], "object_id": e.get("object_id"),
                      "reason_code": "DIRECTLY_CITATION_ELIGIBLE" if e in direct else "NO_VALID_BACKING"}
                     for e in selected]
        cache.update(projection=direct, backings=[], decisions=decisions)
        candidates = []
        for item, decision in zip(selected, decisions):
            if item in direct:
                continue
            locator = item.get("locator") or {}
            if not (locator.get("url") and locator.get("snapshot_date")) or locator.get("section_path"):
                decision["reason_code"] = "INVALID_LOCATOR"
            elif not item.get("object_id"):
                decision["reason_code"] = "CONTENT_RELATION_NOT_ESTABLISHED"
            else:
                candidates.append((item, decision))
        if len(candidates) > 4:
            for _, decision in candidates:
                decision["reason_code"] = "BOUND_EXCEEDED"
            return direct
        if not candidates:
            return direct
        try:
            manifest = json.loads((self.project_root / "data/manifests/source_manifest.json").read_text(encoding="utf-8"))
            documents = manifest["web_documents"]
            if not isinstance(documents, list):
                raise ValueError("invalid web manifest")
            records = self.retriever.storage.read_sphinx_backing([e["object_id"] for e, _ in candidates])
            pages = {p["object_id"]: p for p in records["pages"]}
        except Exception:
            for _, decision in candidates:
                decision["reason_code"] = "LOOKUP_FAILED"
            return direct
        replacements: dict[str, dict[str, Any]] = {}
        additions: list[dict[str, Any]] = []
        for item, decision in candidates:
            try:
                page = pages.get(item["object_id"])
                if not page or page.get("object_type") != "sphinx_page":
                    continue
                docs = [d for d in documents if d.get("doc_id") == item["source_id"]]
                if len(docs) != 1:
                    decision["reason_code"] = "VERSION_MISMATCH"
                    continue
                doc = docs[0]
                snapshot, date = doc["snapshot_hash"], doc["captured_at"][:10]
                version = f"{doc['doc_id']}@{snapshot}"
                loc = item["locator"]
                if (not snapshot or not date or item["source_version_id"] != version
                    or page.get("source_id") != item["source_id"] or page.get("source_version_id") != version
                    or page.get("metadata", {}).get("snapshot_hash") != snapshot
                    or loc.get("snapshot_date") != date or page["locator"].get("snapshot_date") != date
                    or (item.get("metadata") is not None and item["metadata"].get("snapshot_hash") != snapshot)):
                    decision["reason_code"] = "VERSION_MISMATCH"
                    continue
                if (page.get("text") != item["text"] or page["locator"].get("section_path")
                    or item.get("object_type", "sphinx_page") != "sphinx_page"
                    or any(page["locator"].get(k) != loc.get(k) for k in ("path", "url"))
                    or not any(r.get("path") == loc.get("path") and r.get("url") == loc.get("url")
                               for r in doc["records"])):
                    decision["reason_code"] = "CONTENT_RELATION_NOT_ESTABLISHED"
                    continue
                children = records["children"].get(page["object_id"], [])
                if len(children) > 16:
                    decision["reason_code"] = "BOUND_EXCEEDED"
                    continue
                qualified = []
                rejections = []
                for child in children:
                    reason = self._backing_rejection(child, page, item, snapshot, date)
                    if reason:
                        rejections.append({"object_id": child.get("object_id"), "reason_code": reason})
                    else:
                        qualified.append(child)
                decision["candidate_rejections"] = rejections
                if len(qualified) != 1:
                    decision["reason_code"] = "AMBIGUOUS_BACKING" if qualified else "NO_VALID_BACKING"
                    continue
                child = qualified[0]
                backing = Evidence(
                    evidence_id=stable_id(child["object_id"], "ea_exact_backing", prefix="evidence"),
                    object_id=child["object_id"], source_id=child["source_id"],
                    source_version_id=child["source_version_id"], text=child["text"],
                    locator=child["locator"], authority_level=child["authority_level"],
                    retrieval_channels=["ea_exact_backing"], score=0.0,
                ).model_dump(mode="json")
                existing = [e for e in selected if e.get("object_id") == child["object_id"]]
                if existing:
                    # An already-selected identity must agree, not be silently repaired.
                    if len(existing) != 1 or existing[0] not in direct or any(
                        existing[0].get(k) != backing[k] for k in
                        ("source_id", "source_version_id", "text", "locator", "authority_level")
                    ):
                        decision["reason_code"] = "CONTENT_RELATION_NOT_ESTABLISHED"
                        continue
                    backing = existing[0]
                else:
                    if any(e["evidence_id"] == backing["evidence_id"] for e in selected + additions):
                        decision["reason_code"] = "CONTENT_RELATION_NOT_ESTABLISHED"
                        continue
                    replacements[item["evidence_id"]] = backing
                    additions.append(backing)
                start = item["text"].find(child["text"])
                decision.update(reason_code="RESOLVED_EXACT_BACKING", parent_evidence_id=item["evidence_id"],
                                parent_object_id=item["object_id"], backing_evidence_id=backing["evidence_id"],
                                backing_object_id=backing["object_id"], containment_offsets=[start, start + len(child["text"])])
            except Exception:
                decision["reason_code"] = "LOOKUP_FAILED"
        cache["projection"] = [replacements[e["evidence_id"]] if e["evidence_id"] in replacements else e
                               for e in selected if e in direct or e["evidence_id"] in replacements]
        cache["backings"] = additions
        return cache["projection"]

    @staticmethod
    def _backing_rejection(child: dict[str, Any], page: dict[str, Any], selected: dict[str, Any],
                           snapshot: str, date: str) -> str | None:
        if (child.get("source_id") != page["source_id"] or child.get("source_version_id") != page["source_version_id"]
            or child.get("metadata", {}).get("snapshot_hash") != snapshot
            or (child.get("locator") or {}).get("snapshot_date") != date):
            return "VERSION_MISMATCH"
        if (child.get("object_type") != "sphinx_section" or not child.get("object_id")
            or child.get("parent_object_id") != page["object_id"]
            or child.get("metadata", {}).get("parent_object_id") != page["object_id"]):
            return "CONTENT_RELATION_NOT_ESTABLISHED"
        loc = child.get("locator") or {}
        if (not _is_public_claim_citation_eligible(child) or loc.get("path") != selected["locator"].get("path")
            or loc.get("url", "").split("#", 1)[0] != selected["locator"]["url"].split("#", 1)[0]):
            return "INVALID_LOCATOR"
        text = child.get("text")
        if not isinstance(text, str) or not text:
            return "CONTENT_RELATION_NOT_ESTABLISHED"
        if len(text) > 12_000 or child.get("ea_text_length", len(text)) > 12_000:
            return "BOUND_EXCEEDED"
        start = selected["text"].find(text)
        if start < 0 or selected["text"].find(text, start + 1) >= 0:
            return "CONTENT_RELATION_NOT_ESTABLISHED"
        return None

    @staticmethod
    def _qa_evidence(state: QAState) -> list[dict[str, Any]]:
        return [*state["bundle"]["evidence"], *state.get("_ea_cache", {}).get("backings", [])]

    def _answer(self, state: QAState) -> dict[str, Any]:
        question = str(state["question"])
        # Legacy named requirements are authoritative only in legacy mode.  In
        # E1/E2 coverage modes the model-facing generation payload carries none
        # of them: the shared generation prompt instructs the model to satisfy
        # every supplied obligation, so a non-empty payload would let plan-
        # derived requirements shape public content even though downstream
        # enforcement was retired (F2-A3-R1).
        legacy_answer_requirements = _answer_requirements(question, state["bundle"]["plan"])
        answer_requirements = (
            [] if _coverage_shadow(state) else legacy_answer_requirements
        )
        claim_evidence = self._admitted_evidence(state)
        _trace_admission(state, claim_evidence, 0)
        prompt = json.dumps(
            {
                "task": "create_atomic_evidence_bound_claims",
                "untrusted_question": question,
                "runtime_answer_points": _active_runtime_answer_points(state),
                "answer_requirements": answer_requirements,
                "retrieval_plan": {
                    "intent": state["bundle"]["plan"].get("intent"),
                    "resolved_versions": state["bundle"]["plan"].get("resolved_versions", {}),
                    "target_repositories": state["bundle"]["plan"].get("target_repositories", []),
                    "exact_symbols_and_paths": state["bundle"]["plan"].get("symbols", []),
                    "concept_scopes": state["bundle"]["plan"].get("concept_scopes", {}),
                    "premise_corrections": state["bundle"]["plan"].get("premise_corrections", []),
                    "required_boundary_locators": (
                        state["bundle"]["plan"].get("symbols", [])
                        if not _coverage_shadow(state)
                        and state["bundle"]["plan"].get("intent") == "module_structure"
                        and any(
                            "boundary" in str(value).casefold()
                            for value in state["bundle"]["plan"].get("concepts", [])
                        )
                        else []
                    ),
                },
                "untrusted_evidence": claim_evidence,
            },
            ensure_ascii=False,
        )
        draft = self.generation_vertex.generate_json(
            prompt,
            ANSWER_SCHEMA,
            system_instruction=ANSWER_SYSTEM_PROMPT,
            usage_stage="qa_generation",
        )
        _trace(state, "A0_OUTPUT", 0, lambda: {"response": draft,
               "claim_ordinals": list(range(len(draft.get("claims", []))))})
        if _coverage_shadow(state):
            draft = {"claims": _model_claims(list(draft.get("claims", [])))}
        draft = self._augment_planned_locators(draft, state)
        draft = self._augment_required_dataflow_evidence(draft, state)
        # Version scope is deterministic metadata, not a model guess.  It is
        # retained only as internal audit material, and only for a genuine
        # version-disambiguation request.  In particular, ``resolved_versions``
        # is a retrieval whitelist, never an instruction to enumerate every
        # available repository in the user-visible answer.
        question_lower = question.casefold()
        scope_terms = ("commit", "branch", "version conflict", "version differ", "versions disagree")
        if any(term in question_lower for term in scope_terms):
            claims = list(draft.get("claims", []))
            evidence = state["bundle"]["evidence"]
            cited_source_ids = {
                str(item.get("source_id") or "")
                for claim in claims
                if not _internal_claim_reason(claim)
                for evidence_id in claim.get("evidence_ids", [])
                for item in evidence
                if item.get("evidence_id") == evidence_id
            }
            target_repositories = set(
                str(repo) for repo in state["bundle"]["plan"].get("target_repositories", [])
            )
            for repo, sha in state["bundle"]["plan"].get("resolved_versions", {}).items():
                if repo not in cited_source_ids and repo not in target_repositories:
                    continue
                if any(claim.get("claim_id") == f"scope_{repo}" for claim in claims):
                    continue
                source_evidence = [
                    item["evidence_id"]
                    for item in evidence
                    if item.get("source_id") == repo
                    or str(item.get("source_version_id", "")).startswith(f"{repo}@")
                ]
                documentation_evidence = [
                    item["evidence_id"]
                    for item in evidence
                    if "sphinx" in str(item.get("source_id", "")).casefold()
                    and (item.get("locator") or {}).get("snapshot_date")
                ]
                if repo == "pandaroot" and documentation_evidence:
                    claim_text = (
                        "The operational guidance uses the locked PandaRoot Sphinx "
                        "2023-08-25-dev documentation snapshot, while repository behavior "
                        f"is scoped to {repo}@{sha} and remains commit-specific."
                    )
                    evidence_ids = [
                        documentation_evidence[0],
                        *source_evidence[:1],
                    ]
                else:
                    if not source_evidence:
                        continue
                    claim_text = (
                        f"This answer is scoped to the locked source version {repo}@{sha}; "
                        "repository behavior is commit-specific, so current behavior must "
                        "be read from this version."
                    )
                    evidence_ids = source_evidence[:1]
                claims.insert(
                    0,
                    {
                        "claim_id": f"scope_{repo}",
                        "claim_text": claim_text,
                        "evidence_ids": evidence_ids,
                        "answer_point_ids": [],
                    },
                )
            draft["claims"] = claims
        draft["claims"] = _normalise_claim_answer_points(
            _strip_nonessential_external_identifiers(
                list(draft.get("claims", [])), question, state["bundle"]["plan"]
            ),
            question,
        )
        # Keep the full legacy set in state for the unknown-requirement guard
        # and diagnostics; it carries no model-facing authority in coverage
        # modes.
        return {"draft": draft, "answer_requirements": legacy_answer_requirements}

    def _verify(self, state: QAState) -> dict[str, Any]:
        shadow = _coverage_shadow(state)
        satisfaction = _coverage_satisfaction_enabled(state)
        admitted_ids = {e["evidence_id"] for e in self._admitted_evidence(state)} if satisfaction else set()
        runtime_points = _active_runtime_answer_points(state)
        draft = state["draft"]
        evidence = {item["evidence_id"]: item for item in self._qa_evidence(state)}
        errors: list[str] = []
        all_claims = list(draft.get("claims", []))
        claim_audit = list(state.get("claim_audit", []))
        claims: list[dict[str, Any]] = []
        for claim in all_claims:
            internal_reason = _internal_claim_reason(claim)
            if internal_reason:
                claim_audit.append(_claim_audit_record(claim, internal_reason))
                continue
            claims.append(claim)
        claim_errors: dict[str, list[str]] = {}
        claim_ids = [claim.get("claim_id") for claim in claims]
        if not claims:
            errors.append("no user-visible claims")
        if len(claim_ids) != len(set(claim_ids)) or any(not value for value in claim_ids):
            errors.append("claim IDs must be unique and non-empty")
        runtime_answer_point_ids = {item["answer_point_id"] for item in runtime_points}
        expected_code_versions = {
            repo: f"{repo}@{sha}"
            for repo, sha in state["bundle"]["plan"].get("resolved_versions", {}).items()
        }
        retained_claims = state.get("retained_supported_claims") or []
        retained_evidence = state.get("retained_support_evidence") or {}
        for claim in claims:
            claim_id = str(claim.get("claim_id") or "")
            claim_errors.setdefault(claim_id, [])
            is_retained_unchanged = any(
                _claim_matches_retained(claim, ret) for ret in retained_claims
            )

            def _claim_ev(eid: str) -> dict[str, Any]:
                it = evidence.get(eid)
                if it is None and is_retained_unchanged:
                    it = retained_evidence.get(eid)
                return it or {}

            if shadow and (not claim_id or claim_ids.count(claim.get("claim_id")) != 1):
                claim_errors[claim_id].append("claim IDs must be unique and non-empty")
            answer_point_ids = claim.get("answer_point_ids")
            unresolved_locator = shadow and claim.get("_unresolved_locator_mapping") is True
            if not isinstance(answer_point_ids, list) or (not answer_point_ids and not unresolved_locator):
                message = f"claim lacks runtime answer-point mapping: {claim_id}"
                errors.append(message)
                claim_errors[claim_id].append(message)
            elif not set(str(value) for value in answer_point_ids).issubset(runtime_answer_point_ids):
                message = f"claim has invalid runtime answer-point mapping: {claim_id}"
                errors.append(message)
                claim_errors[claim_id].append(message)
            elif shadow and (any(not isinstance(v, str) for v in answer_point_ids)
                             or len(answer_point_ids) != len(set(answer_point_ids))):
                message = f"claim has invalid runtime answer-point mapping: {claim_id}"
                errors.append(message)
                claim_errors[claim_id].append(message)
            evidence_ids = claim.get("evidence_ids", [])
            has_invalid_evidence = False
            if not evidence_ids:
                has_invalid_evidence = True
            else:
                for eid in evidence_ids:
                    if eid in evidence:
                        pass
                    elif is_retained_unchanged and eid in retained_evidence:
                        pass
                    else:
                        has_invalid_evidence = True
                        break
            if has_invalid_evidence:
                message = f"invalid evidence for {claim_id}"
                errors.append(message)
                claim_errors[claim_id].append(message)
            cited_parts: list[str] = []
            for evidence_id in evidence_ids:
                item = _claim_ev(evidence_id)
                if not item:
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
            cited = " ".join(cited_parts)
            for evidence_id in evidence_ids:
                item = _claim_ev(evidence_id)
                if not item:
                    continue
                locator = item.get("locator", {})
                source_id = item.get("source_id")
                if source_id in {"luminosityfit", "pandaroot", "restgas_determination"}:
                    if item.get("source_version_id") != expected_code_versions.get(source_id):
                        message = f"wrong code version {evidence_id}"
                        errors.append(message)
                        claim_errors[claim_id].append(message)
                    if not (locator.get("path") and locator.get("start_line") and locator.get("end_line")):
                        message = f"incomplete code citation {evidence_id}"
                        errors.append(message)
                        claim_errors[claim_id].append(message)
                elif source_id in {"li_2026", "karavdina_2015", "pflueger_2017"} and not locator.get("pdf_page"):
                    message = f"incomplete paper citation {evidence_id}"
                    errors.append(message)
                    claim_errors[claim_id].append(message)
                elif source_id and "sphinx" in source_id and not (locator.get("url") and locator.get("snapshot_date") and locator.get("section_path")):
                    message = f"incomplete web citation {evidence_id}"
                    errors.append(message)
                    claim_errors[claim_id].append(message)
            for token in set(re.findall(r"[A-Za-z_][A-Za-z0-9_:./-]+", claim.get("claim_text", ""))):
                token = _normalise_rejected_identifier_token(token)
                is_path = token.count("/") >= 2 or token.startswith(("macro/", "src/", "data/", "pgenerators/", "model/", "fit/")) or token.endswith(_CODE_DATA_EXTENSIONS)
                if ("::" in token or is_path) and token not in cited:
                    message = f"unsupported identifier {token}"
                    errors.append(message)
                    claim_errors[claim_id].append(message)
        review_evidence_lookup = {item["evidence_id"]: item for item in evidence.values() if "evidence_id" in item}
        if retained_evidence:
            for eid, item in retained_evidence.items():
                review_evidence_lookup.setdefault(eid, item)
        review_evidence = [
            {
                "evidence_id": item.get("evidence_id"),
                "source_id": item.get("source_id"),
                "source_version_id": item.get("source_version_id"),
                "locator": item.get("locator", {}),
                "text": item.get("text", ""),
            }
            for item in review_evidence_lookup.values()
        ]
        answer_requirements = list(
            state.get("answer_requirements")
            or _answer_requirements(str(state.get("question", "")), state["bundle"]["plan"])
        )
        # Full legacy set feeds only the unknown-requirement guard here.  In
        # coverage modes the review payload carries no legacy requirements:
        # answer-point coverage is the sole completeness axis (F2-A3-R1).
        known_requirement_ids = {str(item["id"]) for item in answer_requirements}
        model_answer_requirements = [] if shadow else answer_requirements
        requirement_evidence = (
            {} if shadow else _requirement_evidence(answer_requirements, review_evidence_lookup)
        )
        reviewable_claims = [c for c in claims if not claim_errors.get(str(c.get("claim_id") or ""))] if shadow else claims
        review_prompt = json.dumps(
            {
                "task": "review_claim_support_and_relevance",
                "runtime_answer_points": runtime_points,
                "answer_requirements": model_answer_requirements,
                "requirement_evidence": requirement_evidence,
                "untrusted_claims": _model_claims(reviewable_claims) if shadow else claims,
                "untrusted_evidence": review_evidence,
                **({"untrusted_question": state["question"],
                    "admitted_evidence_ids": [e["evidence_id"] for e in self._admitted_evidence(state)],
                    "coverage_satisfaction_schema_version": COVERAGE_SATISFACTION_SCHEMA_VERSION,
                } if satisfaction else {}),
            },
            ensure_ascii=False,
        )
        review_round = 2 if state.get("revision_count", 0) else 1
        _trace(state, f"V{review_round}_INPUT", review_round, lambda: {
            "model_input": json.loads(review_prompt), "normalized_draft": claims,
            "deterministic_claim_errors": claim_errors})
        review = self.verification_vertex.generate_json(
            review_prompt,
            PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SCHEMA if satisfaction else (ANSWER_POINT_COVERAGE_REVIEW_SCHEMA if shadow else REVIEW_SCHEMA),
            system_instruction=PRODUCTION_COVERAGE_SATISFACTION_REVIEW_SYSTEM_PROMPT if satisfaction else (ANSWER_POINT_COVERAGE_REVIEW_SYSTEM_PROMPT if shadow else EVIDENCE_REVIEW_SYSTEM_PROMPT),
            usage_stage="qa_semantic_verification",
        )
        _trace(state, f"V{review_round}_OUTPUT", review_round, lambda: {"response": review})
        verified_mappings: dict[str, list[str]] = {}
        coverage_review_error = None
        missing_points: list[str] = []
        if shadow:
            try:
                if satisfaction:
                    verified_mappings = _validate_coverage_satisfaction(
                        review, reviewable_claims, runtime_answer_point_ids, known_requirement_ids,
                        review_evidence_lookup, admitted_ids)
                else:
                    verified_mappings = _validate_answer_point_review(
                        review, reviewable_claims, runtime_answer_point_ids, known_requirement_ids)
            except ValueError as exc:
                coverage_review_error = str(exc)
                errors.append(f"invalid answer-point coverage review: {exc}")
                independent = None
                if satisfaction and isinstance(review, dict):
                    # Salvage only independently valid support/mapping judgments,
                    # never manufacture a valid production relationship scope.
                    candidate = {**review,
                        "missing_answer_point_ids": [p["answer_point_id"] for p in runtime_points],
                        "answer_point_coverage": [{"answer_point_id": p["answer_point_id"],
                            "supporting_claim_ids": [], "complete": False} for p in runtime_points]}
                    try:
                        verified_mappings = _validate_answer_point_review(
                            candidate, reviewable_claims, runtime_answer_point_ids, known_requirement_ids)
                        if review["supported"] or review["unsupported_claim_ids"] or review["irrelevant_claim_ids"]:
                            independent = candidate
                    except ValueError:
                        pass
                review = independent or {"supported": False, "unsupported_claim_ids": [c["claim_id"] for c in reviewable_claims],
                          "irrelevant_claim_ids": [], "missing_requirement_ids": [], "reason": str(exc),
                          "missing_answer_point_ids": [p["answer_point_id"] for p in runtime_points]}
            missing_points = list(review["missing_answer_point_ids"])
            errors.extend(f"missing answer point {pid}" for pid in missing_points)
        _trace(state, f"V{review_round}_OUTPUT", review_round, lambda: {
            "validation": {"status": "REJECTED" if coverage_review_error else ("ACCEPTED" if shadow else "NOT_APPLICABLE"),
                           "error": coverage_review_error}}, update=True)
        unsupported = review.get("unsupported_claim_ids", [])
        irrelevant = review.get("irrelevant_claim_ids", [])
        missing_requirements = [str(value) for value in review.get("missing_requirement_ids", [])]
        if not shadow:
            missing_requirements.extend(
                _deterministic_missing_requirement_ids(answer_requirements, claims, evidence)
            )
        known_claim_ids = set(claim_ids)
        for claim_id in unsupported:
            message = f"unsupported claim {claim_id}" if claim_id in known_claim_ids else f"review returned unknown claim {claim_id}"
            errors.append(message)
            if claim_id in known_claim_ids:
                claim_errors.setdefault(claim_id, []).append(message)
        for claim_id in irrelevant:
            message = (
                f"irrelevant claim {claim_id}"
                if claim_id in known_claim_ids
                else f"review returned unknown irrelevant claim {claim_id}"
            )
            errors.append(message)
            if claim_id in known_claim_ids:
                claim_errors.setdefault(claim_id, []).append(message)
        accepted_missing_requirements: list[str] = []
        for requirement_id in missing_requirements:
            if requirement_id not in known_requirement_ids:
                errors.append(f"review returned unknown answer requirement {requirement_id}")
                continue
            if shadow:
                # E1/E2 answer-point coverage owns whole-answer completeness in
                # the coverage modes; the legacy named-requirement contract is a
                # legacy-default bridge and must not act as a second hidden
                # answer key there.
                continue
            accepted_missing_requirements.append(requirement_id)
            errors.append(f"missing answer requirement {requirement_id}")
        # A missing completeness requirement is not a verdict that every
        # already-supported claim is invalid.  Preserve those claims and let
        # the one bounded revision add only the missing factual link.
        # A stale legacy completeness verdict must not fail a coverage-mode
        # answer: if the only structured explanation for supported=false is a
        # set of known (retired-in-coverage) legacy requirement ids while every
        # authoritative axis is clean, treat the aggregate boolean as obsolete.
        # Anything else (no explanation, unknown ids) keeps the conservative
        # global failure.
        stale_legacy_only = (
            shadow
            and bool(missing_requirements)
            and all(requirement_id in known_requirement_ids for requirement_id in missing_requirements)
        )
        if (
            not review["supported"]
            and not unsupported
            and not irrelevant
            and not accepted_missing_requirements
            and not missing_points
            and not stale_legacy_only
        ):
            errors.append(review.get("reason") or "evidence review failed")
        global_review_failure = (
            not review["supported"]
            and not unsupported
            and not irrelevant
            and not accepted_missing_requirements
            and not missing_points
            and not stale_legacy_only
        )
        supported_claims = [
            claim
            for claim in claims
            if claim.get("claim_id")
            and not claim_errors.get(str(claim.get("claim_id")))
            and not global_review_failure
        ]
        unsupported_ids = [
            str(claim.get("claim_id"))
            for claim in claims
            if claim not in supported_claims and claim.get("claim_id")
        ]
        coverage_update = {}
        if shadow:
            if global_review_failure:
                missing_points = [p["answer_point_id"] for p in runtime_points]
            supported_ids = {c["claim_id"] for c in supported_claims}
            mapping_audit = [{
                "claim_id": str(c.get("claim_id") or ""),
                "declared_answer_point_ids": list(c.get("declared_answer_point_ids", c.get("answer_point_ids")) or []),
                "verified_answer_point_ids": verified_mappings.get(c.get("claim_id"), []),
                "evidence_ids": list(c.get("evidence_ids") or []),
                "supported": c.get("claim_id") in supported_ids,
                "rendered": False,
            } for c in claims]
            supported_claims = [{**c,
                "declared_answer_point_ids": list(c.get("declared_answer_point_ids", c.get("answer_point_ids")) or []),
                "answer_point_ids": verified_mappings[c["claim_id"]],
            } for c in supported_claims]
            covered = [p["answer_point_id"] for p in runtime_points if p["answer_point_id"] not in missing_points]
            coverage_update = {"missing_answer_point_ids": missing_points, "answer_point_audit": {
                "mode": state["answer_point_coverage_mode"], "answer_points": runtime_points, "claim_mappings": mapping_audit,
                "covered_answer_point_ids": covered, "missing_answer_point_ids": missing_points,
                "coverage_complete": not missing_points and not coverage_review_error and not global_review_failure,
                "coverage_evaluable": not coverage_review_error and not global_review_failure,
                "review_error": coverage_review_error,
            }}
            if state.get("answer_point_coverage_mode") == "runtime_e1_v2":
                evaluable = not coverage_review_error and not global_review_failure
                if state.get("missing_point_retrieval_count", 0) == 0 and state.get("revision_count", 0) == 0:
                    eligible, reason = self._check_e3_trigger(
                        state,
                        missing_answer_point_ids=missing_points,
                        audit=coverage_update["answer_point_audit"],
                    )
                    if not eligible:
                        coverage_update["e3_trace"] = {
                            "triggered": False,
                            "trigger_reason": reason,
                            "missing_answer_point_ids": missing_points,
                            "missing_answer_points": [p for p in runtime_points if p.get("answer_point_id") in set(missing_points)],
                            "retrieval_objective": None,
                            "missing_point_retrieval_count": 0,
                            "pre_answer_retrieval_count": state.get("retrieval_count", 0),
                            "initial_selected_evidence_ids": [item.get("evidence_id") for item in state.get("bundle", {}).get("evidence", [])],
                            "candidate_pass_provenance": [],
                            "targeted_candidate_object_ids": [],
                            "dedup_result": {},
                            "pass_occurrences": {},
                            "global_fused_candidate_object_ids": [],
                            "globally_selected_evidence_ids": [item.get("evidence_id") for item in state.get("bundle", {}).get("evidence", [])],
                            "global_selected_object_ids": [item.get("object_id") for item in state.get("bundle", {}).get("evidence", [])],
                            "newly_admitted_object_ids": [],
                            "displaced_selected_evidence_ids": [],
                            "retained_support_evidence_ids": [],
                            "retained_supported_claims": [],
                            "selected_evidence_count": len(state.get("bundle", {}).get("evidence", [])),
                            "selected_evidence_budget": getattr(getattr(self.retriever, "policies", None), "final_evidence_limit", 12),
                            "retained_support_context_count": 0,
                            "atomic_update_status": "not_triggered",
                            "no_gain": False,
                            "failure_reason": None,
                            "post_retrieval_missing_point_result": None,
                            "post_retrieval_coverage_evaluable": None,
                            "recovered_answer_point_ids": [],
                            "remaining_missing_answer_point_ids": missing_points,
                        }
                elif state.get("e3_trace") and state["e3_trace"].get("triggered") and state.get("revision_count", 0) >= 1:
                    trace = dict(state["e3_trace"])
                    curr_missing = set(missing_points)
                    prev_missing = trace.get("missing_answer_point_ids", [])
                    if evaluable:
                        recovered = [pid for pid in prev_missing if pid not in curr_missing]
                        trace["post_retrieval_coverage_evaluable"] = True
                        trace["post_retrieval_missing_point_result"] = "complete" if not missing_points else ("partial" if recovered else "unrecovered")
                        trace["recovered_answer_point_ids"] = recovered
                        trace["remaining_missing_answer_point_ids"] = missing_points
                        trace["recovered_on_revision"] = len(recovered) > 0
                    else:
                        trace["post_retrieval_coverage_evaluable"] = False
                        trace["post_retrieval_missing_point_result"] = "unevaluable"
                        trace["recovered_answer_point_ids"] = []
                        trace["remaining_missing_answer_point_ids"] = missing_points
                        trace["recovered_on_revision"] = False
                    coverage_update["e3_trace"] = trace
        if satisfaction:
            relationships = []
            repair_ids = []
            evaluable = not coverage_review_error and not global_review_failure
            if evaluable:
                for point in review["answer_point_coverage"]:
                    if point["scope_status"] == "ESTABLISHED":
                        for check in point["relationship_checks"]:
                            if check["admission_state"] == "ADMITTED_BACKING_AVAILABLE" and not check["satisfied"]:
                                relationships.append({"answer_point_id": point["answer_point_id"],
                                    "relationship_text": check["relationship_text"], "basis": deepcopy(check["basis"])})
                repair_ids = [c["claim_id"] for c in reviewable_claims
                    if c["claim_id"] in unsupported and c["claim_id"] not in irrelevant
                    and c.get("evidence_ids") and set(c["evidence_ids"]) <= admitted_ids][:8]
            coverage_update.update(revisionable_relationships=relationships,
                revisionable_unsupported_claim_ids=repair_ids,
                revisionable_unsupported_claim_mappings={cid: list(verified_mappings[cid]) for cid in repair_ids},
                coverage_blocked=bool(missing_points) or not evaluable,
                coverage_satisfaction_status="VALID" if evaluable else "INVALID")
            coverage_update["answer_point_audit"].update(
                coverage_satisfaction_schema_version=COVERAGE_SATISFACTION_SCHEMA_VERSION,
                answer_point_coverage=deepcopy(review.get("answer_point_coverage", [])) if evaluable else None,
                revisionable_relationships=relationships, revisionable_unsupported_claim_ids=repair_ids)
        return {
            **coverage_update,
            "errors": list(dict.fromkeys(errors)),
            "supported_claims": supported_claims,
            "unsupported_claim_ids": list(dict.fromkeys(unsupported_ids)),
            "missing_requirement_ids": list(dict.fromkeys(accepted_missing_requirements)),
            "answer_requirements": answer_requirements,
            "claim_audit": claim_audit,
        }

    def _revise(self, state: QAState) -> dict[str, Any]:
        shadow = _coverage_shadow(state)
        satisfaction = _coverage_satisfaction_enabled(state)
        runtime_points = _active_runtime_answer_points(state)
        supported = list(state.get("supported_claims", []))
        unsupported_ids = set(state.get("unsupported_claim_ids", []))
        if satisfaction:
            unsupported_ids = set(state.get("revisionable_unsupported_claim_ids", []))
        unsupported_draft = {
            "claims": [
                claim
                for claim in state["draft"].get("claims", [])
                if claim.get("claim_id") in unsupported_ids
            ]
        }
        if satisfaction:
            verified_repair_mappings = state.get("revisionable_unsupported_claim_mappings", {})
            unsupported_draft["claims"] = [
                {**claim, "answer_point_ids": list(verified_repair_mappings.get(claim["claim_id"], []))}
                for claim in unsupported_draft["claims"]
            ]
        answer_requirements = list(
            state.get("answer_requirements")
            or _answer_requirements(str(state["question"]), state["bundle"]["plan"])
        )
        # In E1/E2 coverage modes the legacy named-requirement contract is a
        # non-authoritative bridge; bounded revision there is driven by missing
        # answer points (and unsupported claims), not by named requirements.
        # The model-facing payload carries no legacy requirement authority
        # (F2-A3-R1); the full set stays in state for diagnostics only.
        missing_requirement_ids = (
            [] if shadow else list(state.get("missing_requirement_ids", []))
        )
        model_answer_requirements = [] if shadow else answer_requirements
        claim_evidence = self._admitted_evidence(state)
        _trace_admission(state, claim_evidence, 1)
        requirement_evidence = (
            {}
            if shadow
            else _requirement_evidence(
                [
                    item
                    for item in answer_requirements
                    if str(item["id"]) in set(missing_requirement_ids)
                ],
                {item["evidence_id"]: item for item in claim_evidence},
            )
        )
        prompt = json.dumps(
            {
                "task": "revise_unsupported_claims_once",
                "untrusted_question": state["question"],
                "runtime_answer_points": runtime_points,
                **({
                    "missing_answer_point_ids": list(state.get("missing_answer_point_ids", [])),
                    "missing_answer_points": [p for p in runtime_points if p["answer_point_id"] in state.get("missing_answer_point_ids", [])],
                } if shadow else {}),
                "answer_requirements": model_answer_requirements,
                "missing_requirement_ids": missing_requirement_ids,
                "requirement_evidence": requirement_evidence,
                "revision_scope": (
                    "Add only evidence-backed, user-relevant claims needed to satisfy "
                    + ("missing_answer_point_ids; " if shadow else "missing_requirement_ids; ")
                    + "do not add a claim when evidence does not establish it."
                ),
                "already_verified_claims_do_not_repeat": _model_claims(supported) if shadow else supported,
                "untrusted_draft": {"claims": _model_claims(unsupported_draft["claims"])} if shadow else unsupported_draft,
                "verification_errors": state["errors"],
                "untrusted_evidence": claim_evidence,
            },
            ensure_ascii=False,
        )
        if satisfaction:
            relationships = state.get("revisionable_relationships", [])
            recovery_ids = {b["evidence_id"] for r in relationships for b in r["basis"]}
            recovery_ids.update(eid for c in unsupported_draft["claims"] for eid in c.get("evidence_ids", []))
            point_ids = {r["answer_point_id"] for r in relationships}
            point_ids.update(pid for c in unsupported_draft["claims"] for pid in c.get("answer_point_ids", []))
            points = [p for p in runtime_points if p["answer_point_id"] in point_ids]
            payload = json.loads(prompt)
            payload.update(runtime_answer_points=points,
                missing_answer_point_ids=[p["answer_point_id"] for p in points], missing_answer_points=points,
                revisionable_relationships=relationships,
                revisionable_answer_point_ids=[p["answer_point_id"] for p in points],
                revisionable_answer_points=points,
                revisionable_unsupported_claim_ids=list(state.get("revisionable_unsupported_claim_ids", [])),
                revision_scope="Repair only listed revisionable_relationships and eligible unsupported claims; broad point text is context only.",
                verification_errors=[f"unsupported claim {cid}" for cid in state.get("revisionable_unsupported_claim_ids", [])],
                untrusted_evidence=[e for e in claim_evidence if e["evidence_id"] in recovery_ids])
            prompt = json.dumps(payload, ensure_ascii=False)
        _trace(state, "A1_INPUT", 1, lambda: {"model_input": json.loads(prompt)})
        revised = self.generation_vertex.generate_json(
            prompt,
            ANSWER_SCHEMA,
            system_instruction=PRODUCTION_COVERAGE_SATISFACTION_REVISION_SYSTEM_PROMPT if satisfaction else (ANSWER_POINT_COVERAGE_REVISION_SYSTEM_PROMPT if shadow else REVISION_SYSTEM_PROMPT),
            usage_stage="qa_generation",
        )
        _trace(state, "A1_OUTPUT", 1, lambda: {"response": revised,
               "claim_ordinals": list(range(len(revised.get("claims", []))))})
        if shadow:
            revised = {"claims": _model_claims(list(revised.get("claims", [])))}
        revised_claims = _normalise_claim_answer_points(
            _strip_nonessential_external_identifiers(
                list(revised.get("claims", [])), str(state["question"]), state["bundle"]["plan"]
            ),
            str(state["question"]),
        )
        _trace(state, "A1_OUTPUT", 1, lambda: {"normalized_claims": revised_claims,
               "transform_mapping": [{"input_ordinal": i, "normalized_ordinal": i}
                                     for i in range(len(revised_claims))]}, update=True)
        # F6-A2-FR2 revision discipline: a restatement identical (normalized) to
        # a claim just found unsupported is not a revision — the same text
        # cannot both lack and carry evidential support, so re-entering it
        # would let an unstable re-verdict resurrect a known-unsupported claim
        # as an asserted fact. Substantively narrowed/reworded revisions pass.
        unsupported_texts = {
            str(claim.get("claim_id") or ""): _normalized_claim_text(claim.get("claim_text"))
            for claim in state["draft"].get("claims", [])
            if claim.get("claim_id") and claim.get("claim_id") in set(state.get("unsupported_claim_ids", []))
        }
        merged: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        seen_texts: set[str] = set()
        _trace(state, "A1_POST_MERGE", 1, lambda: {"supported_prefix_input": supported,
               "prefix_dispositions": [], "dispositions": []})
        for prefix_ordinal, claim in enumerate(supported):
            claim_id = str(claim.get("claim_id") or "")
            if not claim_id or claim_id in seen_ids:
                _trace_merge(state, prefix_ordinal, claim_id, None, "OTHER_EXPLICIT_REASON", False,
                             lambda: {"reason_code": "MISSING_ID" if not claim_id else "DUPLICATE_ID"},
                             collection="prefix_dispositions")
                continue
            _trace_merge(state, prefix_ordinal, claim_id, claim_id, "RETAINED", True, lambda: None,
                         collection="prefix_dispositions")
            seen_ids.add(claim_id)
            normalized_text = _normalized_claim_text(claim.get("claim_text"))
            if normalized_text:
                seen_texts.add(normalized_text)
            merged.append(claim)
        _trace(state, "A1_POST_MERGE", 1, lambda: {"supported_prefix": merged}, update=True)
        for ordinal, claim in enumerate(revised_claims):
            claim_id = str(claim.get("claim_id") or "")
            if not claim_id:
                _trace_merge(state, ordinal, claim_id, None, "MISSING_ID", False, lambda: None)
                continue
            normalized_text = _normalized_claim_text(claim.get("claim_text"))
            if (
                claim_id in unsupported_texts
                and normalized_text == unsupported_texts[claim_id]
            ):
                _trace_merge(state, ordinal, claim_id, None, "IDENTICAL_UNSUPPORTED_REJECTED", False,
                             lambda: {"stage": "A1_INPUT", "unsupported_draft_ordinal": next(
                                 i for i, c in enumerate(unsupported_draft["claims"]) if c.get("claim_id") == claim_id),
                                 "claim_id": claim_id})
                continue
            # Post-A5 completeness recovery: the generator may reuse an existing
            # local claim ID for genuinely new content. Discard only an exact
            # restatement of already-present content; keep new content alive
            # under a fresh local ID so the single bounded revision can still
            # recover a missing obligation. Identical-unsupported restatement
            # above stays blocked (F6-A2-FR2 unchanged).
            if normalized_text and normalized_text in seen_texts:
                _trace_merge(state, ordinal, claim_id, None, "NORMALIZED_DUPLICATE", False,
                             lambda: {"stage": "A1_POST_MERGE", "merged_ordinal": next(
                                 i for i, c in enumerate(merged) if _normalized_claim_text(c.get("claim_text")) == normalized_text)})
                continue
            if claim_id in seen_ids:
                suffix = 2
                while f"{claim_id}_r{suffix}" in seen_ids:
                    suffix += 1
                _trace_merge(state, ordinal, claim_id, f"{claim_id}_r{suffix}", "ID_COLLISION_RENAMED", True,
                             lambda: {"stage": "A1_POST_MERGE", "merged_ordinal": next(
                                 i for i, c in enumerate(merged) if c.get("claim_id") == claim_id), "claim_id": claim_id})
                claim_id = f"{claim_id}_r{suffix}"
            else:
                _trace_merge(state, ordinal, claim_id, claim_id, "RETAINED", True, lambda: None)
            seen_ids.add(claim_id)
            if normalized_text:
                seen_texts.add(normalized_text)
            merged.append({**claim, "claim_id": claim_id})
        _trace(state, "A1_POST_MERGE", 1, lambda: {"claims": merged}, update=True)
        return {
            "draft": {"claims": merged},
            "revision_count": state.get("revision_count", 0) + 1,
            "errors": [],
            "supported_claims": [],
            "unsupported_claim_ids": [],
            "missing_requirement_ids": [],
            "answer_requirements": answer_requirements,
        }

    def _compose_verified_answer(self, claims: list[ClaimCitation], *,
                                 _stage_trace: Any = None) -> tuple[str, dict[str, Any]]:
        """F5 bounded readability composer over already verified public claims.

        Exactly one composer call (generation role) and at most one semantic
        review call (verification role), no retries. Every failure falls back
        to the untouched deterministic renderer; the QA request never fails and
        verification_errors are never touched. Diagnostics carry counts and
        fixed reason codes only — never prompt, claim, evidence, or model text.
        """
        trace_state = {"_stage_trace": _stage_trace}
        _trace(trace_state, "C_INPUT", 0, lambda: {"verified_claims": [
            {"claim_id": c.claim_id, "claim_text": c.claim_text} for c in claims],
            "citation_edges": [{"claim_id": c.claim_id, "evidence_ids": c.evidence_ids} for c in claims]})
        fallback_answer = render_verified_answer(claims)

        def _diagnostics(
            *,
            attempted: bool,
            accepted: bool,
            reason: str,
            paragraph_count: int,
            deterministic_error_codes: list[str],
            semantic_review_called: bool,
        ) -> dict[str, Any]:
            result = {
                "attempted": attempted,
                "accepted": accepted,
                "fallback_used": attempted and not accepted,
                "reason": reason,
                "source_claim_count": len(claims),
                "paragraph_count": paragraph_count,
                "deterministic_error_codes": deterministic_error_codes,
                "semantic_review_called": semantic_review_called,
            }
            _trace(trace_state, "C_OUTPUT", 0, lambda: {"outcome": result,
                   "generation_status": "CAPTURED" if attempted and reason != "composer_generation_failed" else ("NOT_CAPTURED" if attempted else "NOT_EXECUTED"),
                   "final_answer_ref": "result.answer"}, update=True)
            return result

        if len(claims) < 2:
            return fallback_answer, _diagnostics(
                attempted=False,
                accepted=False,
                reason="single_claim_bypass",
                paragraph_count=0,
                deterministic_error_codes=[],
                semantic_review_called=False,
            )
        verified_claims = [
            {"claim_id": claim.claim_id, "claim_text": claim.claim_text}
            for claim in claims
        ]
        try:
            composer_output = self.generation_vertex.generate_json(
                json.dumps(
                    {"task": "compose_verified_claims", "verified_claims": verified_claims},
                    ensure_ascii=False,
                ),
                COMPOSER_SCHEMA,
                system_instruction=ANSWER_COMPOSER_SYSTEM_PROMPT,
                usage_stage="qa_composer",
            )
        except Exception:
            return fallback_answer, _diagnostics(
                attempted=True,
                accepted=False,
                reason="composer_generation_failed",
                paragraph_count=0,
                deterministic_error_codes=[],
                semantic_review_called=False,
            )
        _trace(trace_state, "C_OUTPUT", 0, lambda: {"response": composer_output})
        paragraphs = composer_output.get("paragraphs") if isinstance(composer_output, dict) else None
        ok, codes = _validate_composed_paragraphs(paragraphs, claims)
        if not ok:
            return fallback_answer, _diagnostics(
                attempted=True,
                accepted=False,
                reason="deterministic_validation_failed",
                paragraph_count=len(paragraphs) if isinstance(paragraphs, list) else 0,
                deterministic_error_codes=codes,
                semantic_review_called=False,
            )
        try:
            review = self.verification_vertex.generate_json(
                json.dumps(
                    {
                        "task": "review_composed_answer",
                        "verified_claims": verified_claims,
                        "paragraphs": [
                            {"text": paragraph["text"], "source_claim_ids": paragraph["source_claim_ids"]}
                            for paragraph in paragraphs
                        ],
                    },
                    ensure_ascii=False,
                ),
                COMPOSER_REVIEW_SCHEMA,
                system_instruction=ANSWER_COMPOSER_REVIEW_SYSTEM_PROMPT,
                usage_stage="qa_composer",
            )
        except Exception:
            return fallback_answer, _diagnostics(
                attempted=True,
                accepted=False,
                reason="composer_review_failed",
                paragraph_count=len(paragraphs),
                deterministic_error_codes=[],
                semantic_review_called=True,
            )
        _trace(trace_state, "C_OUTPUT", 0, lambda: {"review_response": review}, update=True)
        if not _validate_composer_review(review, len(paragraphs), {claim.claim_id for claim in claims}):
            return fallback_answer, _diagnostics(
                attempted=True,
                accepted=False,
                reason="semantic_review_rejected",
                paragraph_count=len(paragraphs),
                deterministic_error_codes=[],
                semantic_review_called=True,
            )
        return render_composed_answer(paragraphs, claims), _diagnostics(
            attempted=True,
            accepted=True,
            reason="composed",
            paragraph_count=len(paragraphs),
            deterministic_error_codes=[],
            semantic_review_called=True,
        )

    def _finalize(self, state: QAState) -> dict[str, Any]:
        plan = state.get("bundle", {}).get("plan", {})
        composer_diagnostics = None
        c1_incomplete = (_coverage_satisfaction_enabled(state) and state.get("sufficient")
                         and not plan.get("version_conflicts") and state.get("coverage_blocked", False))
        salvageable = (
            state.get("sufficient")
            and not plan.get("version_conflicts")
            and bool(state.get("supported_claims"))
        )
        if not state.get("sufficient") or (state.get("errors") and not salvageable and not c1_incomplete):
            status = QAStatus.VERSION_CONFLICT if plan.get("version_conflicts") else QAStatus.INSUFFICIENT_EVIDENCE
            question = str(state.get("question", ""))
            is_chinese = bool(re.search(r"[\u3400-\u9fff]", question))
            claims: list[ClaimCitation] = []
            cited_evidence: list[dict[str, Any]] = []
            if status == QAStatus.VERSION_CONFLICT:
                conflicts = "; ".join(str(value) for value in plan.get("version_conflicts", []))
                named_identifiers = [
                    value
                    for value in ("event_poca", "POCA_VERTEX_FILE", "restgas_profile")
                    if value.casefold() in question.casefold()
                ]
                subject = f" for {', '.join(named_identifiers)}" if named_identifiers else ""
                if is_chinese:
                    answer = (
                        f"请求的版本与锁定语料冲突（{conflicts}），因此拒绝针对"
                        f"{('、'.join(named_identifiers) if named_identifiers else '该非锁定版本')}"
                        "给出确定性实现说明，避免混用版本。"
                    )
                else:
                    answer = (
                        f"The requested version conflicts with the locked corpus ({conflicts}); "
                        f"the request{subject} is refused rather than mixing versions."
                    )
            elif any(
                str(error).startswith("exact future runtime outcome or checksum cannot be established")
                for error in state.get("errors", [])
            ):
                replacement = _refusal_basis_evidence(state, kind="future_runtime")
                if replacement:
                    location = _refusal_basis_location(replacement)
                    subject = _refusal_basis_subject(question, replacement)
                    claims = [
                        ClaimCitation(
                            claim_id="future_runtime_refusal_basis",
                            claim_text=(
                                f"The locked code at {location} defines the available producer/workflow context for {subject}, "
                                "but cannot determine an exact value or checksum for a future runtime artifact "
                                "before that execution occurs."
                            ),
                            evidence_ids=[str(replacement["evidence_id"])],
                        )
                    ]
                    cited_evidence = [replacement]
                answer = (
                    "The requested exact future runtime outcome or checksum cannot be verified before execution. "
                    "/ 无法在执行前验证所请求的精确未来运行结果或校验和。"
                )
                if claims:
                    answer += "\n" + render_verified_answer(claims)
            elif any(
                str(error).startswith("open-domain universal proof is unsupported")
                for error in state.get("errors", [])
            ):
                replacement = _refusal_basis_evidence(state, kind="universal_proof")
                if replacement:
                    location = _refusal_basis_location(replacement)
                    subject = _refusal_basis_subject(question, replacement)
                    claims = [
                        ClaimCitation(
                            claim_id="universal_proof_refusal_basis",
                            claim_text=(
                                f"The cited theory/paper evidence at {location} reports finite or evaluated {subject} cases, "
                                "not an explicit theorem or proof over every possible case."
                            ),
                            evidence_ids=[str(replacement["evidence_id"])],
                        )
                    ]
                    cited_evidence = [replacement]
                answer = (
                    "The available corpus does not provide an explicit same-domain formal theorem or proof "
                    "for this open-domain universal claim. / 现有语料没有提供与该开放域全称主张同一领域的明确形式定理或证明。"
                )
                if claims:
                    answer += "\n" + render_verified_answer(claims)
            elif any(
                str(error).startswith("unsupported requested symbol: ")
                for error in state.get("errors", [])
            ):
                # Generic unsupported-requested-symbol refusal (F2-A4): the
                # locked-catalog absence is the authority; the requested symbol
                # comes from the structured error, and any optional basis claim
                # cites only query-relevant selected evidence.  No fixed
                # replacement locator and no asserted substitute implementation.
                error = next(
                    str(error)
                    for error in state.get("errors", [])
                    if str(error).startswith("unsupported requested symbol: ")
                )
                requested = error.split(":", 1)[1].strip()
                basis = _refusal_basis_evidence(state, kind="unsupported_symbol")
                if basis:
                    location = _refusal_basis_location(basis)
                    subject = _refusal_basis_subject(question, basis)
                    claims = [
                        ClaimCitation(
                            claim_id="unsupported_symbol_context",
                            claim_text=(
                                f"The cited locked code at {location} documents {subject}."
                            ),
                            evidence_ids=[str(basis["evidence_id"])],
                        )
                    ]
                    cited_evidence = [basis]
                refusal = (
                    f"锁定语料未定义 {requested}，因此无法验证该符号的实现细节。"
                    if is_chinese
                    else f"The locked corpus does not define {requested}, so its implementation details cannot be verified."
                )
                answer = refusal + ("\n" + render_verified_answer(claims) if claims else "")
            elif any(
                str(error).startswith("unsupported requested API symbol:")
                for error in state.get("errors", [])
            ):
                error = next(
                    str(error)
                    for error in state.get("errors", [])
                    if str(error).startswith("unsupported requested API symbol:")
                )
                requested = error.split(":", 1)[1].strip()
                # The locked-catalog API absence is the refusal authority.  A
                # cited replacement must be evidence whose own locator matches
                # the requested owner; no historical header path receives
                # preference, and the claim asserts only what the evidence
                # supports.
                replacement = next(
                    (
                        item
                        for item in state.get("bundle", {}).get("evidence", [])
                        if requested.rsplit("::", 1)[0].split("::", 1)[-1]
                        in str((item.get("locator") or {}).get("path") or "")
                        or requested.rsplit("::", 1)[0]
                        == str((item.get("locator") or {}).get("symbol") or "")
                    ),
                    None,
                )
                if replacement:
                    owner = requested.rsplit("::", 1)[0].split("::", 1)[-1]
                    location = _refusal_basis_location(replacement)
                    claims = [
                        ClaimCitation(
                            claim_id="unsupported_api_guard",
                            claim_text=(
                                f"The cited locked code at {location} documents {owner}, "
                                f"but does not establish the exact requested API signature {requested}."
                            ),
                            evidence_ids=[replacement["evidence_id"]],
                        )
                    ]
                    cited_evidence = [replacement]
                answer = (
                    f"The locked corpus does not declare the exact API signature {requested}; "
                    "the request is therefore insufficiently evidenced."
                )
                if claims:
                    answer += "\n" + render_verified_answer(claims)
            elif any(
                str(error).startswith("runtime artifact records cannot be reconstructed")
                for error in state.get("errors", [])
            ):
                # The deleted-runtime refusal may cite only already-selected
                # code/workflow evidence that overlaps an identifier-like
                # artifact anchor from the live question; the base refusal is
                # artifact-neutral.
                basis = _refusal_basis_evidence(state, kind="deleted_runtime")
                if basis:
                    location = _refusal_basis_location(basis)
                    subject = _refusal_basis_subject(question, basis)
                    claims = [
                        ClaimCitation(
                            claim_id="runtime_artifact_guard",
                            claim_text=(
                                f"The cited locked code at {location} documents {subject}, "
                                "but source code does not contain deleted runtime records."
                            ),
                            evidence_ids=[str(basis["evidence_id"])],
                        )
                    ]
                    cited_evidence = [basis]
                answer = "Deleted runtime records cannot be reconstructed from source code alone."
                if claims:
                    answer += "\n" + render_verified_answer(claims)
            else:
                answer = "证据不足，无法给出可验证的确定性回答。" if is_chinese else "The evidence is insufficient for a verifiable, definitive answer."
            result = QAResult(
                status=status,
                answer=answer,
                claims=claims,
                evidence=cited_evidence,
                verification_errors=state.get("errors", []),
                resolved_versions=plan.get("resolved_versions", {}),
            )
        else:
            # Always render the verifier's user-visible subset.  ``draft``
            # intentionally still retains diagnostic-only synthetic claims so
            # they can be audited, but it must never become the public answer.
            claim_items = list(state.get("supported_claims", []))
            # ``answer_point_ids`` is private workflow metadata.  Strip it at
            # the public DTO boundary rather than widening ClaimCitation/API.
            claims = [
                ClaimCitation.model_validate(
                    {
                        key: item.get(key)
                        for key in ("claim_id", "claim_text", "evidence_ids")
                    }
                )
                for item in claim_items
            ]
            cited_ids = {evidence_id for claim in claims for evidence_id in claim.evidence_ids}
            bundle_evidence = [
                item
                for item in self._qa_evidence(state)
                if item.get("evidence_id") in cited_ids
            ]
            included_ids = {item.get("evidence_id") for item in bundle_evidence}
            retained_cited = []
            if state.get("answer_point_coverage_mode") == "runtime_e1_v2":
                retained_map = state.get("retained_support_evidence") or {}
                for eid in sorted(cited_ids):
                    if eid not in included_ids and eid in retained_map:
                        retained_cited.append(retained_map[eid])
                        included_ids.add(eid)
            cited_evidence = [*bundle_evidence, *retained_cited]
            # F5: the optional bounded composer runs only here; every failure
            # mode falls back to the deterministic renderer below.
            if c1_incomplete:
                answer = (render_verified_answer(claims) + "\n\n" if claims else "") + C1_INCOMPLETE_NOTICE
            elif claims:
                if state.get("_stage_trace") is not None:
                    answer, composer_diagnostics = self._compose_verified_answer(
                        claims, _stage_trace=state["_stage_trace"])
                else:
                    answer, composer_diagnostics = self._compose_verified_answer(claims)
            else:
                answer = render_verified_answer(claims)
            result = QAResult(
                status=QAStatus.INSUFFICIENT_EVIDENCE if c1_incomplete else QAStatus.ANSWERED,
                answer=answer,
                claims=claims,
                evidence=cited_evidence,
                verification_errors=state.get("errors", []),
                resolved_versions=plan.get("resolved_versions", {}),
            )
        visible_mapping_audit = [
            {
                "claim_id": str(claim.get("claim_id") or ""),
                "answer_point_ids": list(claim.get("answer_point_ids") or []),
                "filter_reason": "rendered",
            }
            for claim in state.get("supported_claims", [])
            if not _internal_claim_reason(claim)
        ]
        coverage_update = {}
        if _coverage_shadow(state):
            points = _active_runtime_answer_points(state)
            audit = dict(state.get("answer_point_audit") or {
                "mode": state["answer_point_coverage_mode"], "answer_points": points, "claim_mappings": [],
                "covered_answer_point_ids": [],
                "missing_answer_point_ids": [p["answer_point_id"] for p in points],
                "coverage_complete": False, "coverage_evaluable": False,
            })
            rendered_ids = {c.claim_id for c in result.claims} if result.status == QAStatus.ANSWERED or c1_incomplete else set()
            audit["claim_mappings"] = [{**m, "rendered": m["supported"] and m["claim_id"] in rendered_ids}
                                       for m in audit["claim_mappings"]]
            coverage_update["answer_point_audit"] = audit
        return {
            **coverage_update,
            "result": result.model_dump(mode="json"),
            "claim_audit": [
                *state.get("claim_audit", []),
                *visible_mapping_audit,
            ],
            "composer_diagnostics": composer_diagnostics,
        }

    def run(self, question: str) -> QAResult:
        return QAResult.model_validate(self.run_detailed(question)["result"])

    def run_detailed(self, question: str) -> dict[str, Any]:
        """Execute the selected normal QA mode with sanitized diagnostics."""
        return self._run_detailed(question, mode=DEFAULT_ANSWER_POINT_MODE)

    def run_answer_point_coverage_diagnostic(self, question: str) -> dict[str, Any]:
        """Explicit E1-v2 shadow coverage; not exposed through normal QA/API."""
        return self._run_detailed(question, mode="shadow_e1_v2")

    def _run_detailed(self, question: str, *, mode: str = "legacy_question_core",
                      capture_stage_trace: bool = False) -> dict[str, Any]:
        """Internal paired-evaluation seam; not a public API selector."""
        if mode not in _ANSWER_POINT_MODES:
            raise ValueError(f"unsupported answer-point mode: {mode}")
        coverage_shadow = mode in {
            "shadow_e1_v2",
            "runtime_e1_v2",
            "production_answer_obligations_v1",
        }
        started = time.perf_counter()
        stats_before = self._stats_snapshot()
        initial: QAState = {"question": question, "_ea_cache": {}}
        trace_initialization_failed = False
        if capture_stage_trace:
            try:
                initial["_stage_trace"] = _QAStageTrace()
            except Exception:
                trace_initialization_failed = True
        decomposition = None
        decomposition_ms = 0
        if coverage_shadow:
            decomposition_started = time.perf_counter()
            decomposition = self.decompose_question(question)
            if mode == "production_answer_obligations_v1":
                decomposition = {**decomposition, "mode": "production_authoritative"}
            initial.update(answer_point_coverage_mode=mode, runtime_answer_points=decomposition["points"])
            initial["runtime_answer_points"] = _active_runtime_answer_points(initial)
            decomposition_ms = int(round((time.perf_counter() - decomposition_started) * 1000))
        state = self.graph.invoke(initial)
        duration_ms = int(round((time.perf_counter() - started) * 1000))
        result = QAResult.model_validate(state["result"])
        bundle = state.get("bundle", {})
        diagnostics = {
            "plan": bundle.get("plan", {}),
            "rankings": bundle.get("rankings", {}),
            "fusion_scores": bundle.get("fusion_scores", {}),
            "reranked_object_ids": bundle.get("reranked_object_ids", []),
            "ranked_object_ids": bundle.get("ranked_object_ids", []),
            "excluded": bundle.get("excluded", []),
            "selected_evidence": bundle.get("evidence", []),
            "selected_evidence_ids": [
                item.get("evidence_id") for item in bundle.get("evidence", [])
            ],
            "retrieval_count": state.get("retrieval_count", 0),
            "initial_retrieval_count": 1,
            "targeted_retrieval_count": state.get("retrieval_count", 0),
            "selected_evidence_count": len(bundle.get("evidence", [])),
            "revision_count": state.get("revision_count", 0),
            "verification_errors": state.get("errors", []),
            "claim_audit": state.get("claim_audit", []),
        }
        diagnostics["model_roles"] = self._model_roles_diagnostics()
        if state.get("composer_diagnostics") is not None:
            diagnostics["composer"] = state["composer_diagnostics"]
        if coverage_shadow:
            diagnostics.update(question_decomposition=decomposition, answer_point_audit=state["answer_point_audit"])
        if mode == "runtime_e1_v2":
            e3_trace = state.get("e3_trace")
            if e3_trace is None:
                plan = bundle.get("plan", {})
                reason = "version_conflicts" if plan.get("version_conflicts") else "insufficient_evidence"
                e3_trace = {
                    "triggered": False,
                    "trigger_reason": reason,
                    "missing_answer_point_ids": [],
                    "missing_answer_points": [],
                    "retrieval_objective": None,
                    "missing_point_retrieval_count": state.get("missing_point_retrieval_count", 0),
                    "pre_answer_retrieval_count": state.get("retrieval_count", 0),
                    "initial_selected_evidence_ids": [item.get("evidence_id") for item in bundle.get("evidence", [])],
                    "candidate_pass_provenance": [],
                    "targeted_candidate_object_ids": [],
                    "dedup_result": {},
                    "pass_occurrences": {},
                    "global_fused_candidate_object_ids": [],
                    "globally_selected_evidence_ids": [item.get("evidence_id") for item in bundle.get("evidence", [])],
                    "global_selected_object_ids": [item.get("object_id") for item in bundle.get("evidence", [])],
                    "newly_admitted_object_ids": [],
                    "displaced_selected_evidence_ids": [],
                    "retained_support_evidence_ids": [],
                    "retained_supported_claims": [],
                    "selected_evidence_count": len(bundle.get("evidence", [])),
                    "selected_evidence_budget": getattr(getattr(self.retriever, "policies", None), "final_evidence_limit", 12),
                    "retained_support_context_count": 0,
                    "atomic_update_status": "not_triggered",
                    "no_gain": False,
                    "failure_reason": None,
                    "post_retrieval_missing_point_result": None,
                    "post_retrieval_coverage_evaluable": None,
                    "recovered_answer_point_ids": [],
                    "remaining_missing_answer_point_ids": [],
                }
            diagnostics["e3_trace"] = e3_trace
        if capture_stage_trace:
            try:
                diagnostics["qa_stage_trace"] = (
                    _trace_incomplete("CAPTURE_INITIALIZATION_FAILED") if trace_initialization_failed
                    else initial["_stage_trace"].finish()
                )
            except Exception:
                diagnostics["qa_stage_trace"] = _trace_incomplete("CAPTURE_ASSEMBLY_FAILED")
        return {
            "result": result.model_dump(mode="json"),
            "diagnostics": diagnostics,
            "node_timings_ms": {**state.get("node_timings_ms", {}),
                                **({"question_decomposition": decomposition_ms} if coverage_shadow else {}),
                                "workflow": duration_ms},
            "model_usage": self._model_usage_delta(stats_before),
        }

    def _role_clients(self) -> list[Any]:
        """Distinct role clients in deterministic order; a shared legacy injected
        client appearing as both roles is counted once."""
        return list(dict.fromkeys((self.generation_vertex, self.verification_vertex)))

    def _stats_snapshot(self) -> dict[str, int]:
        snapshot: dict[str, int] = {}
        seen = False
        for client in self._role_clients():
            read = getattr(client, "stats_snapshot", None)
            if not callable(read):
                continue
            seen = True
            for key, value in dict(read()).items():
                snapshot[key] = snapshot.get(key, 0) + int(value)
        return snapshot if seen else {}

    def _model_usage_delta(self, before: dict[str, int]) -> dict[str, int]:
        after = self._stats_snapshot()
        usage = {
            key: after.get(key, 0) - before.get(key, 0)
            for key in after.keys() | before.keys()
        }
        for key in ("model_calls", "token_usage", "generation_calls", "embedding_calls"):
            usage.setdefault(key, 0)
        return usage

    def _model_roles_diagnostics(self) -> dict[str, Any]:
        """Internal role-identity receipt. No project IDs, credentials, prompts, or responses."""
        def role_model(client: Any) -> str | None:
            # Report the model this client actually sends generate_json calls to
            # (settings.generation_model on the role client), not the base
            # verification_model configuration field, which only names the model
            # used to derive the verification client (F4-R1).
            settings = getattr(client, "settings", None)
            if settings is None:
                return None
            return getattr(settings, "generation_model", None)
        generation_model = role_model(self.generation_vertex)
        verification_model = role_model(self.verification_vertex)
        return {
            "answer_generation_model": generation_model,
            "semantic_verification_model": verification_model,
            "same_model_id": (
                generation_model == verification_model
                if generation_model is not None and verification_model is not None
                else None
            ),
            "distinct_client_paths": self.generation_vertex is not self.verification_vertex,
        }

    @staticmethod
    def _timed_node(name: str, node: Any) -> Any:
        """Preserve node behavior while recording cumulative execution time."""
        def timed(state: QAState) -> dict[str, Any]:
            started = time.perf_counter()
            output = node(state)
            timings = dict(state.get("node_timings_ms", {}))
            timings[name] = timings.get(name, 0) + int(
                round((time.perf_counter() - started) * 1000)
            )
            return {**output, "node_timings_ms": timings}

        return timed
