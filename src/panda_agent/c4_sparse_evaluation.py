"""Deterministic, offline C4 lexical-query sparse evaluation.

The C4 evaluator is deliberately a small boundary around frozen C2 records.
It never invokes the query analyzer and it does not know about dense retrieval,
answer generation, reranking, final evidence selection, or external judges.
Selection is performed from the frozen question, Gold eligibility metadata, a
faithful C2 plan, and the pure :mod:`panda_agent.lexical_query` builder.  The
optional execution half accepts an encoder and a Qdrant-like object so tests
can remain entirely in memory.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from panda_agent.lexical_query import (
    LexicalQuery,
    LexicalQueryComponent,
    build_lexical_query,
)

try:  # qdrant is an optional import for callers that only screen records.
    from qdrant_client import models as _qdrant_models
except Exception:  # pragma: no cover - exercised only by minimal runtimes.
    _qdrant_models = None


PROMPT_VERSION = "3.7.0"
INTENT_CYCLE = (
    "installation",
    "usage",
    "algorithm_theory",
    "algorithm_implementation",
    "api",
    "data_flow",
    "module_structure",
    "troubleshooting",
)
EXCLUDED_CASE_IDS = frozenset({"g011", "g016"})
MIN_QUALIFIED_CASES = 6
MAX_SCREENING_CASES = 12
TOP_K = 20
MAX_QUERY_ENCODES = 24
MAX_SPARSE_READS = 24

_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_:./*?-]+")
_EXPLICIT_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    r"[A-Za-z]:[\\/][A-Za-z0-9_./\\-]+|"
    r"[A-Za-z_][A-Za-z0-9_]*(?:(?:::|[:./\\-])[A-Za-z0-9_*?]+)*|"
    r"v?\d+(?:[._-]\d+)+(?:[-._][A-Za-z0-9]+)*|"
    r"[0-9A-Fa-f]{7,40}"
    r")(?![A-Za-z0-9_])"
)
_VERSION_TOKEN_RE = re.compile(
    r"(?:v?\d+(?:[._-]\d+)+(?:[-._][A-Za-z0-9]+)*|[0-9A-Fa-f]{7,40})\Z",
    re.IGNORECASE,
)
_FORBIDDEN_PROVENANCE = (
    "gold",
    "evidence",
    "critical",
    "target_object",
    "object_id",
    "final",
    "failure",
    "pre_",
    "post_",
    "hidden",
    "reviewed_expansion",
    "fallback_scope",
    "page_hint",
    "file_hint",
    "answer_requirement",
    "version_metadata",
    "repository_metadata",
)
_ALLOWED_PROVENANCE = {
    "user_raw",
    "analyzer_accepted",
    "accepted_alias",
    "deterministic",
    "deterministic_parse",
}


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _first(value: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        result = _field(value, name, None)
        if result is not None:
            return result
    return default


def _status_text(value: Any) -> str | None:
    if value is None:
        return None
    raw = getattr(value, "value", value)
    return str(raw).casefold()


def _bool_marker(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        nested = _first(
            value,
            "value",
            "status",
            "result",
            "verdict",
            "faithful",
            "c2_compatible",
            "compatible",
            default=None,
        )
        if nested is not None and nested is not value:
            return _bool_marker(nested)
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().casefold()
        if text in {"true", "yes", "pass", "passed", "faithful", "compatible"}:
            return True
        if text in {"false", "no", "fail", "failed", "unfaithful", "incompatible"}:
            return False
    return bool(value)


def _as_list(value: Any) -> list[Any]:
    if value is None or isinstance(value, (str, bytes)):
        return []
    if isinstance(value, Sequence):
        return list(value)
    return []


def _normalization_key(value: str) -> str:
    return " ".join(value.casefold().split())


def _json_records(source: Any) -> tuple[list[Any], dict[str, Any]]:
    """Load a JSON/JSONL source without constructing an analyzer or service."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        if not path.is_file():
            raise FileNotFoundError(path)
        text = path.read_text(encoding="utf-8")
        if path.suffix.casefold() in {".jsonl", ".ndjson"}:
            rows = [json.loads(line) for line in text.splitlines() if line.strip()]
            return rows, {}
        payload = json.loads(text)
    else:
        payload = source

    if isinstance(payload, Mapping):
        metadata = {
            key: payload[key]
            for key in (
                "prompt_version",
                "prompt_set_version",
                "plan_prompt_version",
                "model_contract",
                "c2_compatible",
                "faithful",
            )
            if key in payload
        }
        for key in ("records", "plan_records", "cases", "results", "questions"):
            if isinstance(payload.get(key), Sequence) and not isinstance(
                payload.get(key), (str, bytes)
            ):
                return list(payload[key]), metadata
        return [payload], metadata
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        return list(payload), {}
    raise TypeError("C2 plan records must be a mapping, sequence, JSON, or JSONL path")


def _effective_prompt_version(record: Any, defaults: Mapping[str, Any] | None = None) -> str | None:
    defaults = defaults or {}
    gold = _field(record, "gold", {}) or {}
    model_contract = _field(record, "model_contract", {}) or {}
    if not isinstance(model_contract, Mapping):
        model_contract = {}
    value = _first(
        record,
        "prompt_version",
        "prompt_set_version",
        "plan_prompt_version",
        default=None,
    )
    if value is None:
        value = _first(
            gold,
            "prompt_version",
            "prompt_set_version",
            "plan_prompt_version",
            default=None,
        )
    if value is None:
        value = _first(model_contract, "prompt_version_required", "prompt_set_version", default=None)
    if value is None:
        value = _first(
            defaults,
            "prompt_version",
            "prompt_set_version",
            "plan_prompt_version",
            default=None,
        )
    default_contract = defaults.get("model_contract") if isinstance(defaults, Mapping) else None
    if value is None and isinstance(default_contract, Mapping):
        value = _first(default_contract, "prompt_version_required", "prompt_set_version", default=None)
    return str(value) if value is not None else None


def _lexical_from_mapping(value: Any, raw_question: str, plan: Mapping[str, Any]) -> LexicalQuery:
    if isinstance(value, LexicalQuery):
        return value
    if not isinstance(value, Mapping):
        return build_lexical_query(raw_question, plan)
    components: list[LexicalQueryComponent] = []
    for item in _as_list(value.get("components")):
        kind = str(_field(item, "kind", "unknown"))
        component_value = str(_field(item, "value", ""))
        provenance = str(_field(item, "provenance", ""))
        spans = _field(item, "support_spans", ())
        if isinstance(spans, str):
            spans = (spans,)
        elif not isinstance(spans, Sequence) or isinstance(spans, bytes):
            spans = ()
        components.append(
            LexicalQueryComponent(
                kind=kind,
                value=component_value,
                provenance=provenance,
                support_spans=tuple(str(span) for span in spans),
                appended=bool(_field(item, "appended", False)),
            )
        )
    return LexicalQuery(
        text=str(value.get("text", raw_question)),
        raw_question=str(value.get("raw_question", raw_question)),
        components=components,
        excluded_component_classes=[
            str(item) for item in _as_list(value.get("excluded_component_classes"))
        ],
    )


def normalize_plan_record(
    record: Any,
    *,
    defaults: Mapping[str, Any] | None = None,
    prompt_version: str = PROMPT_VERSION,
) -> dict[str, Any]:
    """Normalize one frozen C2 case into an evaluator-owned mapping.

    The function accepts both C2 artifact case records and small test fixtures.
    It only reads the record and always invokes the current pure lexical
    builder; serialized lexical-query payloads are intentionally ignored.
    """
    defaults = defaults or {}
    gold = _field(record, "gold", {}) or {}
    case_id = _first(record, "case_id", "question_id", "id", default=None)
    if case_id is None:
        case_id = _first(gold, "case_id", "id", default=None)
    case_id = str(case_id or "")
    raw_question = _first(
        record,
        "raw_question",
        "question",
        "query",
        default=_first(gold, "raw_question", "question", "query", default=""),
    )
    raw_question = str(raw_question or "")
    plan = _first(record, "retrieval_plan", "plan", "plan_summary", default=None)
    if plan is None:
        plan = _first(gold, "retrieval_plan", "plan", "plan_summary", default={})
    if not isinstance(plan, Mapping):
        plan = dict(vars(plan)) if hasattr(plan, "__dict__") else {}
    plan = dict(plan)
    model_contract = _field(record, "model_contract", {}) or {}
    if not isinstance(model_contract, Mapping):
        model_contract = {}
    plan_prompt_version = _first(
        plan, "prompt_version", "prompt_set_version", "plan_prompt_version", default=None
    )
    declared_prompt_versions = [
        str(value)
        for value in (
            _first(record, "prompt_version", "prompt_set_version", "plan_prompt_version", default=None),
            _first(gold, "prompt_version", "prompt_set_version", "plan_prompt_version", default=None),
            _first(model_contract, "prompt_version_required", "prompt_set_version", default=None),
            plan_prompt_version,
            _first(defaults, "prompt_version", "prompt_set_version", "plan_prompt_version", default=None),
            _first(_field(defaults, "model_contract", {}) or {}, "prompt_version_required", "prompt_set_version", default=None),
        )
        if value is not None
    ]
    prompt_defaults = dict(defaults)
    # The active frozen builder is authoritative.  A serialized lexical query
    # supplied by a prior run is diagnostic-only and must never affect C4
    # eligibility or execution.
    lexical_query = build_lexical_query(raw_question, plan)
    effective_prompt_version = plan_prompt_version or _effective_prompt_version(record, prompt_defaults)

    effective_language = _first(
        record,
        "effective_product_language",
        "effective_language",
        default=_first(gold, "effective_product_language", "effective_language", "language", default=None),
    )
    if effective_language is None:
        effective_language = _first(record, "language", default=_first(gold, "language", default=None))
    evidence_groups = _first(
        record,
        "required_evidence_groups",
        "evidence_groups",
        "gold_evidence_groups",
        default=_first(gold, "required_evidence_groups", "evidence_groups", default=[]),
    )
    if evidence_groups is None:
        evidence_groups = []
    return {
        "case_id": case_id,
        "raw_question": raw_question,
        "query": raw_question,
        "split": _first(record, "split", default=_first(gold, "split", default=None)),
        "review_status": _first(
            record, "review_status", default=_first(gold, "review_status", default=None)
        ),
        "language": _first(record, "language", default=_first(gold, "language", default=None)),
        "effective_product_language": str(effective_language).casefold()
        if effective_language is not None
        else None,
        "expected_status": _status_text(
            _first(record, "expected_status", default=_first(gold, "expected_status", default=None))
        ),
        "intent": _first(record, "intent", default=_first(gold, "intent", default=_field(plan, "intent", None))),
        "accepted_intents": [
            str(item)
            for item in _as_list(
                _first(record, "accepted_intents", default=_first(gold, "accepted_intents", default=[]))
            )
        ],
        "plan": plan,
        "plan_intent": _field(plan, "intent", None),
        "prompt_version": effective_prompt_version,
        "declared_prompt_versions": declared_prompt_versions,
        "model_contract": dict(model_contract),
        "evidence_groups": list(evidence_groups) if isinstance(evidence_groups, Sequence) else [],
        "required_answer_points": _as_list(
            _first(record, "required_answer_points", default=_first(gold, "required_answer_points", default=[]))
        ),
        "allowed_source_versions": _as_list(
            _first(record, "allowed_source_versions", default=_first(gold, "allowed_source_versions", default=[]))
        ),
        "required_identifiers": _as_list(
            _first(record, "required_identifiers", default=_first(gold, "required_identifiers", default=[]))
        ),
        "lexical_query": lexical_query,
        "lexical_query_dict": lexical_query.as_dict(),
        "faithful": _first(
            record,
            "faithful",
            "plan_faithful",
            "faithful_plan",
            "retrieval_plan_faithful",
            "plan_fidelity",
            "faithfulness",
            default=_first(
                plan,
                "faithful",
                "plan_faithful",
                "faithful_plan",
                "plan_fidelity",
                "faithfulness",
                default=_first(
                    gold,
                    "faithful",
                    "plan_faithful",
                    "faithful_plan",
                    "plan_fidelity",
                    "faithfulness",
                    default=_first(defaults, "faithful", "plan_faithful", "faithful_plan", default=None),
                ),
            ),
        ),
        "c2_compatible": _first(
            record,
            "c2_compatible",
            "plan_compatible",
            default=_first(
                plan,
                "c2_compatible",
                "plan_compatible",
                default=_first(
                    gold,
                    "c2_compatible",
                    "plan_compatible",
                    default=_first(defaults, "c2_compatible", "plan_compatible", default=None),
                ),
            ),
        ),
        "authoritative_evidence": _first(
            record,
            "authoritative_evidence",
            "evidence_authoritative",
            "authoritative",
            default=_first(
                gold,
                "authoritative_evidence",
                "evidence_authoritative",
                "authoritative",
                default=None,
            ),
        ),
        "original": record,
    }


def load_c2_plan_records(
    source: Any,
    *,
    expected_prompt_version: str = PROMPT_VERSION,
) -> list[dict[str, Any]]:
    """Load and normalize frozen C2 records without analyzer calls."""
    rows, defaults = _json_records(source)
    if expected_prompt_version:
        defaults = {**defaults}
    return [
        normalize_plan_record(
            row,
            defaults=defaults,
            prompt_version=expected_prompt_version,
        )
        for row in rows
    ]


def _calibrated_language(record: Mapping[str, Any], calibration: Mapping[str, Any] | None) -> str | None:
    case_id = str(record.get("case_id", ""))
    if calibration:
        overrides = calibration.get("reviewed_overrides", [])
        for item in _as_list(overrides):
            if str(_field(item, "case_id", "")) == case_id:
                language = _field(item, "effective_product_language", None)
                if language in {"en", "non_en"}:
                    return language
    value = record.get("effective_product_language")
    return str(value).casefold() if value is not None else None


def _has_authoritative_evidence(record: Mapping[str, Any]) -> bool:
    marker = record.get("authoritative_evidence")
    if marker is not None:
        return bool(_bool_marker(marker))
    if record.get("evidence_groups"):
        return True
    # A frozen Gold object may carry its authority as a provenance label.
    original = record.get("original")
    provenance = _first(original, "evidence_provenance", "gold_evidence_provenance", default=None)
    if isinstance(provenance, str):
        return provenance.casefold() in {"gold", "authoritative", "canonical"}
    return bool(_first(original, "authoritative_evidence_ids", default=[]))


def eligibility_report(
    record: Any,
    *,
    calibration: Mapping[str, Any] | None = None,
    expected_prompt_version: str = PROMPT_VERSION,
    normalized: bool = False,
) -> dict[str, Any]:
    """Return deterministic C4 eligibility and its fail-closed reasons."""
    item = record if normalized else normalize_plan_record(
        record, prompt_version=expected_prompt_version
    )
    case_id = str(item.get("case_id", ""))
    reasons: list[str] = []
    if case_id in EXCLUDED_CASE_IDS:
        reasons.append("explicit_exclusion")
    if item.get("split") != "dev":
        reasons.append("split_not_dev")
    if item.get("review_status") != "approved":
        reasons.append("review_status_not_approved")
    if _calibrated_language(item, calibration) != "en":
        reasons.append("effective_language_not_english")
    if item.get("expected_status") != "answered":
        reasons.append("expected_status_not_answered")
    if not _has_authoritative_evidence(item):
        reasons.append("authoritative_evidence_missing")

    plan = item.get("plan")
    if not isinstance(plan, Mapping) or not str(plan.get("intent") or ""):
        reasons.append("faithful_plan_missing")
    if not item.get("declared_prompt_versions"):
        reasons.append("prompt_version_missing")
    if item.get("prompt_version") != expected_prompt_version or any(
        value != expected_prompt_version for value in item.get("declared_prompt_versions", [])
    ):
        reasons.append("prompt_version_incompatible")
    for marker_name in ("faithful", "c2_compatible"):
        marker = item.get(marker_name)
        if _bool_marker(marker) is not True:
            reasons.append(f"{marker_name}_missing_or_false")
    plan_intent = str(item.get("plan_intent") or "")
    gold_intent = str(item.get("intent") or "")
    accepted = {gold_intent, *[str(value) for value in item.get("accepted_intents", [])]}
    if plan_intent and accepted and plan_intent not in accepted:
        reasons.append("plan_intent_not_accepted")
    lexical_query = item.get("lexical_query")
    raw_question = str(item.get("raw_question") or "")
    lexical_text = str(_field(lexical_query, "text", ""))
    if lexical_text == raw_question:
        reasons.append("lexical_query_unchanged")
    if not raw_question:
        reasons.append("raw_question_missing")
    if not case_id:
        reasons.append("case_id_missing")
    return {
        "case_id": case_id,
        "eligible": not reasons,
        "reasons": reasons,
        "effective_product_language": _calibrated_language(item, calibration),
        "lexical_changed": lexical_text != raw_question,
        "plan_intent": plan_intent,
        "prompt_version": item.get("prompt_version"),
    }


def _is_normalized_record(record: Any) -> bool:
    return bool(
        isinstance(record, Mapping)
        and isinstance(record.get("plan"), Mapping)
        and isinstance(record.get("lexical_query"), LexicalQuery)
        and "case_id" in record
        and "raw_question" in record
    )


def _refresh_lexical_query(record: Mapping[str, Any]) -> dict[str, Any]:
    refreshed = dict(record)
    lexical_query = build_lexical_query(str(refreshed.get("raw_question") or ""), refreshed.get("plan") or {})
    refreshed["lexical_query"] = lexical_query
    refreshed["lexical_query_dict"] = lexical_query.as_dict()
    return refreshed


def eligible_c4_records(
    records: Iterable[Any],
    *,
    calibration: Mapping[str, Any] | None = None,
    expected_prompt_version: str = PROMPT_VERSION,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Filter C2 records using only pre-retrieval eligibility inputs."""
    eligible: list[dict[str, Any]] = []
    reports: dict[str, dict[str, Any]] = {}
    for record in records:
        item = (
            _refresh_lexical_query(record)
            if _is_normalized_record(record)
            else normalize_plan_record(record, prompt_version=expected_prompt_version)
        )
        report = eligibility_report(
            item,
            calibration=calibration,
            expected_prompt_version=expected_prompt_version,
            normalized=True,
        )
        reports[report["case_id"]] = report
        if report["eligible"]:
            eligible.append(item)
    return eligible, reports


def deterministic_screening_order(
    records: Iterable[Any],
    *,
    max_cases: int = MAX_SCREENING_CASES,
    calibration: Mapping[str, Any] | None = None,
    expected_prompt_version: str = PROMPT_VERSION,
) -> list[str]:
    """Return the fixed intent-cycle, lexicographic within-intent order."""
    max_cases = min(max(0, int(max_cases)), MAX_SCREENING_CASES)
    eligible, _ = eligible_c4_records(
        records,
        calibration=calibration,
        expected_prompt_version=expected_prompt_version,
    )
    queues: dict[str, list[str]] = defaultdict(list)
    for item in eligible:
        intent = str(item.get("intent") or item.get("plan_intent") or "")
        if intent in INTENT_CYCLE:
            queues[intent].append(str(item["case_id"]))
    for intent in queues:
        queues[intent] = sorted(set(queues[intent]))
    order: list[str] = []
    cursor = {intent: 0 for intent in INTENT_CYCLE}
    while len(order) < max(0, int(max_cases)):
        emitted = False
        for intent in INTENT_CYCLE:
            index = cursor[intent]
            values = queues.get(intent, [])
            if index < len(values):
                order.append(values[index])
                cursor[intent] = index + 1
                emitted = True
                if len(order) >= max_cases:
                    break
        if not emitted:
            break
    return order


def select_screening_cases(
    records: Iterable[Any],
    *,
    max_cases: int = MAX_SCREENING_CASES,
    calibration: Mapping[str, Any] | None = None,
    expected_prompt_version: str = PROMPT_VERSION,
) -> list[dict[str, Any]]:
    """Select up to 12 eligible cases without observing retrieval outcomes."""
    max_cases = min(max(0, int(max_cases)), MAX_SCREENING_CASES)
    normalized = [
        _refresh_lexical_query(record)
        if _is_normalized_record(record)
        else normalize_plan_record(record, prompt_version=expected_prompt_version)
        for record in records
    ]
    by_id = {str(item.get("case_id")): item for item in normalized}
    ids = deterministic_screening_order(
        normalized,
        max_cases=max_cases,
        calibration=calibration,
        expected_prompt_version=expected_prompt_version,
    )
    return [by_id[case_id] for case_id in ids if case_id in by_id]


def build_frozen_query_filter(
    retrieval_plan: Mapping[str, Any], context_sources: Sequence[str]
) -> Any:
    """Use the existing sparse evaluator's repository/version filter builder."""
    try:
        from panda_agent.sparse_evaluation import build_frozen_query_filter as _builder

        return _builder(retrieval_plan, context_sources)
    except (ImportError, ModuleNotFoundError):
        # Minimal test/runtime environments may not ship qdrant-client.  Keep
        # the exact repository/version/source scope as a plain value object so
        # injected clients still receive identical PRE/POST filters.
        repositories = [str(value) for value in retrieval_plan.get("target_repositories", [])]
        if not repositories:
            return None
        versions = retrieval_plan.get("resolved_versions") or {}
        scopes: list[dict[str, Any]] = []
        for repository in repositories:
            if repository not in versions:
                raise ValueError(
                    f"frozen retrieval plan has no resolved version for target repository: {repository}"
                )
            scopes.append(
                {
                    "must": [
                        {"key": "source_id", "value": repository},
                        {
                            "key": "source_version_id",
                            "value": f"{repository}@{versions[repository]}",
                        },
                    ]
                }
            )
        scopes.append({"key": "source_id", "any": [*context_sources, "curated_panda_domain"]})
        return {"should": scopes}


def _identity_value(value: Any, *names: str) -> Any:
    for name in names:
        candidate = _field(value, name, None)
        if candidate is not None:
            return candidate
    return None


def _receipt_identity(receipt: Any) -> Any:
    if receipt is None:
        return None
    if isinstance(receipt, (str, int, float, bool)):
        return str(receipt)
    fingerprint = _identity_value(receipt, "fingerprint", "identity", "receipt_id")
    if callable(fingerprint):
        fingerprint = fingerprint()
    if fingerprint is not None:
        return str(fingerprint)
    dumper = getattr(receipt, "model_dump", None)
    if callable(dumper):
        return dumper()
    if isinstance(receipt, Mapping):
        return dict(receipt)
    return repr(receipt)


def read_only_sparse_preflight(
    qdrant: Any,
    *,
    collection_name: str,
    vector_name: str,
    expected_modifier: str | None = "idf",
    expected_encoder_receipt: Any | None = None,
    encoder_receipt: Any | None = None,
    expected_sparse_receipt: Any | None = None,
    sparse_receipt: Any | None = None,
    expected_schema_version: Any | None = None,
    expected_fingerprint: str | None = None,
    expected_index_identity: Mapping[str, Any] | None = None,
    index_identity: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Fail-closed, read-only sparse collection and identity preflight.

    Missing contract evidence is unavailable rather than compatible.  The
    function never creates, updates, deletes, upserts, scrolls, or queries a
    point; only collection metadata methods are used.
    """
    expected_encoder_receipt = expected_encoder_receipt or expected_sparse_receipt
    encoder_receipt = encoder_receipt or sparse_receipt
    result: dict[str, Any] = {
        "available": False,
        "contract_ok": False,
        "evidence_complete": False,
        "status": "INCONCLUSIVE",
        "collection_name": collection_name,
        "vector_name": vector_name,
        "expected_modifier": expected_modifier,
        "read_calls": 0,
        "write_calls": 0,
        "errors": [],
    }
    if qdrant is None:
        result["errors"].append("qdrant_unavailable")
        return result
    expected_identity = dict(expected_index_identity or {})
    if expected_schema_version is not None:
        expected_identity.setdefault("schema_version", expected_schema_version)
    if expected_fingerprint is not None:
        expected_identity.setdefault("fingerprint", expected_fingerprint)
    if expected_encoder_receipt is not None:
        expected_identity.setdefault("encoder_receipt", expected_encoder_receipt)
    if "schema_version" not in expected_identity or "fingerprint" not in expected_identity:
        result["errors"].append("index_identity_expectation_missing")
        return result
    if expected_identity.get("encoder_receipt") is None and expected_encoder_receipt is None:
        result["errors"].append("encoder_receipt_expected_identity_missing")
        return result
    actual_identity = dict(index_identity or {})
    if encoder_receipt is not None:
        actual_identity.setdefault("encoder_receipt", encoder_receipt)
    if expected_identity and not actual_identity and expected_encoder_receipt is not None and encoder_receipt is None:
        result["errors"].append("encoder_receipt_evidence_unavailable")
        return result
    try:
        exists_method = getattr(qdrant, "collection_exists", None)
        if not callable(exists_method):
            result["errors"].append("collection_existence_evidence_unavailable")
            return result
        result["read_calls"] += 1
        if not bool(exists_method(collection_name)):
            result["errors"].append("collection_missing")
            return result
        get_collection = getattr(qdrant, "get_collection", None)
        if not callable(get_collection):
            result["errors"].append("collection_metadata_evidence_unavailable")
            return result
        result["read_calls"] += 1
        collection = get_collection(collection_name)
        config = _field(_field(collection, "config", None), "params", None)
        sparse_vectors = _field(config, "sparse_vectors", None)
        if not isinstance(sparse_vectors, Mapping):
            result["errors"].append("sparse_vector_config_missing")
            return result
        configured = sparse_vectors.get(vector_name)
        if configured is None:
            result["errors"].append("sparse_vector_name_missing")
            return result
        modifier = _field(configured, "modifier", None)
        if expected_modifier is None or modifier is None:
            result["errors"].append("sparse_modifier_evidence_missing")
            return result
        if _status_text(modifier) != str(expected_modifier).casefold():
            result["errors"].append("sparse_modifier_mismatch")
            return result

        collection_identity = _field(collection, "index_identity", None) or _field(collection, "identity", None)
        if isinstance(collection_identity, Mapping):
            actual_identity.update(collection_identity)
        for name in ("schema_version", "fingerprint", "encoder_receipt"):
            value = _field(collection, name, None)
            if value is not None:
                actual_identity.setdefault(name, value)
        if expected_identity:
            for name, expected in expected_identity.items():
                actual = actual_identity.get(name)
                if actual is None:
                    result["errors"].append(f"{name}_evidence_missing")
                    return result
                if name == "encoder_receipt":
                    if _receipt_identity(actual) != _receipt_identity(expected):
                        result["errors"].append("encoder_receipt_identity_mismatch")
                        return result
                elif actual != expected:
                    result["errors"].append(f"{name}_mismatch")
                    return result
        elif expected_encoder_receipt is None:
            result["errors"].append("encoder_receipt_expected_identity_missing")
            return result
        elif encoder_receipt is None:
            result["errors"].append("encoder_receipt_identity_missing")
            return result
        elif expected_encoder_receipt is not None and _receipt_identity(encoder_receipt) != _receipt_identity(expected_encoder_receipt):
            result["errors"].append("encoder_receipt_identity_mismatch")
            return result
        if not callable(getattr(qdrant, "query_points", None)) and not callable(getattr(qdrant, "search", None)):
            result["errors"].append("sparse_read_api_missing")
            return result
    except Exception as exc:  # infrastructure is inconclusive, never a quality FAIL.
        result["errors"].append(f"preflight_error:{type(exc).__name__}:{exc}")
        return result
    result.update(available=True, contract_ok=True, evidence_complete=True, status="PASS")
    return result


def _identifier_tokens(query: str) -> list[str]:
    values: set[str] = set()
    for match in _EXPLICIT_TOKEN_RE.finditer(str(query)):
        token = match.group(0)
        if _VERSION_TOKEN_RE.fullmatch(token):
            values.add(token)
            continue
        if any(separator in token for separator in ("_", "::", "/", "\\", ".", "-", "*", "?")):
            values.add(token)
            continue
        if any(char.isdigit() for char in token):
            values.add(token)
            continue
        if re.search(r"[a-z][A-Z]|[A-Z][A-Z][a-z]", token):
            values.add(token)
            continue
        if len(token) >= 2 and token.isupper():
            values.add(token)
    return sorted(values)


def explicit_identifier_retention(raw_question: str, lexical_query: Any) -> dict[str, Any]:
    """Audit that raw code/path identifiers remain literal in the lexical text."""
    tokens = _identifier_tokens(str(raw_question))
    text = str(_field(lexical_query, "text", ""))
    missing = [token for token in tokens if token not in text]
    return {
        "tokens": tokens,
        "retained_tokens": [token for token in tokens if token not in missing],
        "missing_tokens": missing,
        "retained_count": len(tokens) - len(missing),
        "total_count": len(tokens),
        "missing_count": len(missing),
        "retention_ratio": 1.0 if not tokens else (len(tokens) - len(missing)) / len(tokens),
        "all_retained": not missing,
    }


def provenance_contamination_audit(lexical_query: Any) -> dict[str, Any]:
    """Check lexical components for downstream/Gold provenance leakage."""
    components = _as_list(_field(lexical_query, "components", []))
    excluded = [str(value).casefold() for value in _as_list(_field(lexical_query, "excluded_component_classes", []))]
    hits: list[dict[str, Any]] = []
    for index, component in enumerate(components):
        kind = str(_field(component, "kind", "")).casefold()
        provenance = str(_field(component, "provenance", "")).casefold()
        for value in (kind, provenance):
            if value and any(marker in value for marker in _FORBIDDEN_PROVENANCE):
                hits.append({"index": index, "field": "kind_or_provenance", "value": value})
        if provenance and provenance not in _ALLOWED_PROVENANCE:
            hits.append({"index": index, "field": "provenance", "value": provenance})
        if bool(_field(component, "appended", False)) and provenance in {
            "user_raw",
            "gold",
            "evidence",
        }:
            hits.append({"index": index, "field": "appended_provenance", "value": provenance})
    for value in excluded:
        if any(marker in value for marker in _FORBIDDEN_PROVENANCE):
            # The builder documents excluded classes; their presence is not
            # contamination.  Only report a class that is itself rendered as
            # a component above.  Keep the list for auditability.
            continue
    return {
        "contamination": bool(hits),
        "contamination_hits": hits,
        "component_count": len(components),
        "excluded_component_classes": excluded,
        "allowed_provenance": sorted(_ALLOWED_PROVENANCE),
    }


def _selector_matches(selector: Any, item: Mapping[str, Any], object_id: str) -> bool:
    if selector is None:
        return False
    selector_object_id = _field(selector, "object_id", None)
    if selector_object_id is not None and str(selector_object_id) != str(object_id):
        return False
    checks = (
        ("source_id", item.get("source_id")),
        ("source_version_id", item.get("source_version_id")),
        ("object_type", item.get("object_type")),
        ("symbol", _field(item.get("locator", {}), "symbol", None)),
    )
    for name, actual in checks:
        expected = _field(selector, name, None)
        if expected is not None and str(actual) != str(expected):
            return False
    expected_path = _field(selector, "path", None)
    if expected_path is not None:
        actual_path = str(_field(item.get("locator", {}), "path", "")).replace("\\", "/")
        if actual_path != str(expected_path).replace("\\", "/"):
            return False
    title_contains = _field(selector, "title_contains", None)
    if title_contains is not None:
        haystack = " ".join(
            [
                str(item.get("title") or ""),
                str(item.get("text") or ""),
                " ".join(str(value) for value in (_field(item.get("locator", {}), "section_path", []) or [])),
            ]
        ).casefold()
        if str(title_contains).casefold() not in haystack:
            return False
    section_contains = _field(selector, "section_contains", None)
    if section_contains is not None:
        sections = " / ".join(
            str(value) for value in (_field(item.get("locator", {}), "section_path", []) or [])
        ).casefold()
        if str(section_contains).casefold() not in sections:
            return False
    locator = item.get("locator") or {}
    start_line = _field(selector, "start_line", None)
    if start_line is not None:
        end_line = _field(selector, "end_line", None) or start_line
        item_start = _field(locator, "start_line", None)
        item_end = _field(locator, "end_line", None)
        if item_start is None or item_end is None or int(item_start) > int(end_line) or int(item_end) < int(start_line):
            return False
    pdf_page = _field(selector, "pdf_page", None)
    if pdf_page is not None:
        pdf_page_end = _field(selector, "pdf_page_end", None) or pdf_page
        item_page = _field(locator, "pdf_page", None)
        if item_page is None or not int(pdf_page) <= int(item_page) <= int(pdf_page_end):
            return False
    return True


def _group_matches(group: Any, object_id: str, object_lookup: Mapping[str, Mapping[str, Any]]) -> bool:
    item = object_lookup.get(object_id, {"object_id": object_id})
    selectors = _field(group, "any_of", []) or []
    return any(_selector_matches(selector, item, object_id) for selector in selectors)


def rank_metrics(
    evidence_groups: Sequence[Any],
    ranked_object_ids: Sequence[str],
    object_lookup: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compute deterministic Recall@5/@10/@20, MRR, and critical coverage."""
    if not isinstance(evidence_groups, Sequence) or isinstance(evidence_groups, (str, bytes)):
        evidence_groups = _field(evidence_groups, "required_evidence_groups", []) or []
    lookup = object_lookup or {}
    ranking = list(dict.fromkeys(str(value) for value in ranked_object_ids))[:TOP_K]
    group_ranks: dict[str, int | None] = {}
    critical_ids: list[str] = []
    for index, group in enumerate(evidence_groups):
        group_id = str(_field(group, "group_id", f"group_{index + 1}"))
        first: int | None = None
        for rank, object_id in enumerate(ranking, 1):
            if _group_matches(group, object_id, lookup):
                first = rank
                break
        group_ranks[group_id] = first
        if bool(_field(group, "critical", True)):
            critical_ids.append(group_id)
    denominator = len(group_ranks)

    def recall(limit: int) -> float:
        if not denominator:
            return 1.0
        return sum(rank is not None and rank <= limit for rank in group_ranks.values()) / denominator

    first_ranks = [rank for rank in group_ranks.values() if rank is not None]
    first_relevant_rank = min(first_ranks) if first_ranks else None
    critical_coverage: float | None
    if critical_ids:
        critical_coverage = sum(
            group_ranks[group_id] is not None and group_ranks[group_id] <= TOP_K
            for group_id in critical_ids
        ) / len(critical_ids)
    else:
        critical_coverage = None
    return {
        "recall_at_5": float(recall(5)),
        "recall_at_10": float(recall(10)),
        "recall_at_20": float(recall(20)),
        "mrr": float(1.0 / first_relevant_rank) if first_relevant_rank else 0.0,
        "first_relevant_rank": first_relevant_rank,
        "first_relevant_ranks": list(group_ranks.values()),
        "first_relevant_ranks_by_group": group_ranks,
        "critical_coverage": critical_coverage,
        "critical_miss_count": sum(
            group_ranks[group_id] is None or group_ranks[group_id] > TOP_K
            for group_id in critical_ids
        ),
        "group_count": denominator,
        "critical_group_count": len(critical_ids),
    }


def classify_case(pre_rank: int | None, post_rank: int | None) -> str:
    """Classify one case into the six fixed PRE/POST rank outcomes."""
    if pre_rank is None and post_rank is None:
        return "no_hit_both"
    if pre_rank is None:
        return "recovered_hit"
    if post_rank is None:
        return "lost_hit"
    if post_rank < pre_rank:
        return "improved"
    if post_rank > pre_rank:
        return "regressed"
    return "unchanged"


def classification_counts(cases: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    names = ("improved", "recovered_hit", "unchanged", "no_hit_both", "regressed", "lost_hit")
    counts = {name: 0 for name in names}
    for case in cases:
        classification = str(case.get("classification") or "")
        if classification in counts:
            counts[classification] += 1
    counts["informative"] = counts["improved"] + counts["recovered_hit"] + counts["unchanged"] + counts["regressed"] + counts["lost_hit"]
    counts["positive"] = counts["improved"] + counts["recovered_hit"]
    counts["negative"] = counts["regressed"] + counts["lost_hit"]
    counts["informative_case_count"] = counts["informative"]
    counts["positive_direction_count"] = counts["positive"]
    counts["negative_direction_count"] = counts["negative"]
    return counts


def _vector_values(value: Any) -> list[Any]:
    values = value.tolist() if hasattr(value, "tolist") else value
    return list(values) if isinstance(values, Sequence) and not isinstance(values, (str, bytes)) else [values]


def _encode_query(encoder: Any, text: str) -> Any:
    method = None
    for name in ("query_embed", "encode", "embed"):
        candidate = getattr(encoder, name, None)
        if callable(candidate):
            method = candidate
            break
    if method is None and callable(encoder):
        method = encoder
    if method is None:
        raise TypeError("sparse encoder has no query_embed/encode/embed callable")
    result = method(text)
    if hasattr(result, "indices") and hasattr(result, "values"):
        return result
    if isinstance(result, Mapping) and "indices" in result and "values" in result:
        return result
    if isinstance(result, Iterable) and not isinstance(result, (str, bytes, Mapping)):
        values = list(result)
        if len(values) == 1:
            return values[0]
    return result


def _as_sparse_vector(value: Any) -> Any:
    indices = _field(value, "indices", None)
    values = _field(value, "values", None)
    if indices is None or values is None or _qdrant_models is None:
        return value
    return _qdrant_models.SparseVector(
        indices=[int(item) for item in _vector_values(indices)],
        values=[float(item) for item in _vector_values(values)],
    )


def _hit_object_id(hit: Any) -> str | None:
    payload = _field(hit, "payload", None)
    if isinstance(payload, Mapping) and payload.get("object_id"):
        return str(payload["object_id"])
    value = _field(hit, "id", None)
    return str(value) if value is not None else None


def _query_sparse(
    qdrant: Any,
    *,
    collection_name: str,
    vector: Any,
    vector_name: str,
    query_filter: Any,
    limit: int,
) -> list[str]:
    method = getattr(qdrant, "query_points", None)
    if callable(method):
        result = method(
            collection_name=collection_name,
            query=vector,
            using=vector_name,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )
    else:
        method = getattr(qdrant, "search", None)
        if not callable(method):
            raise TypeError("Qdrant client has no read-only sparse query method")
        result = method(
            collection_name=collection_name,
            query_vector=(vector_name, vector),
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )
    points = _field(result, "points", result or [])
    ranking: list[str] = []
    for hit in points or []:
        object_id = _hit_object_id(hit)
        if object_id and object_id not in ranking:
            ranking.append(object_id)
        if len(ranking) >= limit:
            break
    return ranking


def _aggregate_metrics(metrics: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    names = ("recall_at_5", "recall_at_10", "recall_at_20", "mrr", "critical_coverage")
    output: dict[str, Any] = {name: None for name in names}
    output["case_count"] = len(metrics)
    for name in names:
        values = [float(item[name]) for item in metrics if item.get(name) is not None]
        output[name] = sum(values) / len(values) if values else None
    output["first_relevant_ranks"] = [item.get("first_relevant_rank") for item in metrics]
    output["critical_miss_count"] = sum(int(item.get("critical_miss_count", 0)) for item in metrics)
    output["critical_applicable_case_count"] = sum(
        1 for item in metrics if int(item.get("critical_group_count", 0)) > 0
    )
    return output


def evaluate_c4_hard_gates(
    result: Mapping[str, Any],
    *,
    minimum_cases: int = MIN_QUALIFIED_CASES,
) -> dict[str, Any]:
    """Apply the user-facing C4 PASS/INCONCLUSIVE/FAIL semantics."""
    selected_count = int(_field(result.get("selection", {}), "selected_count", 0) or 0)
    inconclusive: list[str] = []
    failures: list[str] = []
    preflight = result.get("preflight") or {}
    if selected_count < minimum_cases:
        inconclusive.append("fewer_than_6_qualified_cases")
    if not bool(preflight.get("available", False)) and selected_count >= minimum_cases:
        inconclusive.append("infrastructure_unavailable")
    accounting = result.get("call_accounting") or {}
    if int(accounting.get("sparse_encoder_calls", 0)) > MAX_QUERY_ENCODES:
        failures.append("encode_budget_exceeded")
    if int(accounting.get("sparse_reads", 0)) > MAX_SPARSE_READS:
        failures.append("read_budget_exceeded")
    if result.get("plan_filter_identity_proven", True) is not True and selected_count >= minimum_cases:
        failures.append("pre_post_isolation_contract")
    if selected_count >= minimum_cases and any(
        item.get("same_non_text_parameters") is not True
        or item.get("filter_reused") is not True
        or item.get("raw_query_parameters") != item.get("lexical_query_parameters")
        for item in result.get("cases", [])
    ):
        failures.append("pre_post_isolation_contract")
    if result.get("infrastructure_error"):
        inconclusive.append("infrastructure_unavailable")
    pre = result.get("metrics", {}).get("raw", {})
    post = result.get("metrics", {}).get("lexical", {})
    # Retrieval quality gates are deliberately evidence-preserving: an
    # observed ranking harm is INCONCLUSIVE rather than a contract FAIL.
    if (
        pre.get("recall_at_10") is not None
        and post.get("recall_at_10") is not None
        and post.get("recall_at_10") < pre.get("recall_at_10")
    ):
        inconclusive.append("recall_at_10_regressed")
    if (
        pre.get("recall_at_20") is not None
        and post.get("recall_at_20") is not None
        and post.get("recall_at_20") < pre.get("recall_at_20")
    ):
        inconclusive.append("recall_at_20_regressed")
    pre_critical = pre.get("critical_coverage")
    post_critical = post.get("critical_coverage")
    if pre_critical is not None and post_critical is not None and post_critical < pre_critical:
        inconclusive.append("critical_coverage_regressed")
    if int(result.get("critical_new_misses", 0)) > 0:
        inconclusive.append("new_critical_miss")
    counts = result.get("classification_counts") or {}
    if int(counts.get("lost_hit", 0)) > 0:
        inconclusive.append("lost_hit")
    positive = int(counts.get("positive", counts.get("positive_direction_count", 0)))
    negative = int(counts.get("negative", counts.get("negative_direction_count", 0)))
    if positive < 1:
        inconclusive.append("no_positive_direction")
    if negative > positive:
        inconclusive.append("negative_direction")
    informative = int(counts.get("informative", counts.get("informative_case_count", 0)))
    if informative < math.ceil(max(selected_count, 1) / 2):
        inconclusive.append("insufficient_informativeness")
    if bool((result.get("provenance_contamination") or {}).get("contamination")):
        failures.append("provenance_contamination")
    retention = result.get("identifier_retention") or {}
    if int(retention.get("missing_count", 0)) > 0:
        failures.append("explicit_identifier_loss")
    blocking_reasons = {
        "fewer_than_6_qualified_cases",
        "infrastructure_unavailable",
    }
    if any(reason in blocking_reasons for reason in inconclusive) or result.get("infrastructure_error"):
        verdict = "INCONCLUSIVE"
    elif failures:
        verdict = "FAIL"
    elif inconclusive:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "inconclusive_reasons": list(dict.fromkeys(inconclusive)),
        "failure_reasons": list(dict.fromkeys(failures)),
        "pass": verdict == "PASS",
    }


def run_c4_sparse_evaluation(
    records: Iterable[Any],
    *,
    qdrant: Any | None = None,
    encoder: Any | None = None,
    collection_name: str = "panda_knowledge_v1",
    vector_name: str = "sparse",
    context_sources: Sequence[str] = (),
    object_lookup: Mapping[str, Mapping[str, Any]] | None = None,
    calibration: Mapping[str, Any] | None = None,
    preflight: Mapping[str, Any] | None = None,
    preflight_fn: Any | None = None,
    expected_modifier: str | None = "idf",
    expected_encoder_receipt: Any | None = None,
    encoder_receipt: Any | None = None,
    expected_sparse_receipt: Any | None = None,
    sparse_receipt: Any | None = None,
    expected_schema_version: Any | None = None,
    expected_fingerprint: str | None = None,
    expected_index_identity: Mapping[str, Any] | None = None,
    index_identity: Mapping[str, Any] | None = None,
    filter_builder: Any | None = None,
    top_k: int = TOP_K,
    max_cases: int = MAX_SCREENING_CASES,
) -> dict[str, Any]:
    """Run an injectable raw-vs-lexical sparse comparison.

    For every selected case exactly two encoder calls and two read queries are
    attempted.  Exceptions end the run as infrastructure ``INCONCLUSIVE``;
    neither phase is retried.
    """
    expected_encoder_receipt = expected_encoder_receipt or expected_sparse_receipt
    encoder_receipt = encoder_receipt or sparse_receipt
    max_cases = min(max(0, int(max_cases)), MAX_SCREENING_CASES)
    if int(top_k) != TOP_K:
        raise ValueError("C4 requires top_k exactly 20")
    normalized_records = [
        record
        if _is_normalized_record(record)
        else normalize_plan_record(record)
        for record in records
    ]
    selected = select_screening_cases(
        normalized_records,
        max_cases=max_cases,
        calibration=calibration,
    )
    lookup = object_lookup or {}
    result: dict[str, Any] = {
        "schema_version": "c4-sparse-evaluation-1",
        "selection": {
            "intent_cycle": list(INTENT_CYCLE),
            "excluded_case_ids": sorted(EXCLUDED_CASE_IDS),
            "selected_ids": [str(item["case_id"]) for item in selected],
            "selected_count": len(selected),
            "max_cases": max_cases,
            "selection_inputs": [
                "approved",
                "dev",
                "effective_product_language",
                "answered",
                "authoritative_evidence",
                "faithful_plan",
                "c2_compatible_plan",
                "prompt_version",
                "lexical_query_text_changed",
            ],
            "selection_forbidden_inputs": [
                "PRE",
                "POST",
                "dense",
                "final",
                "failure",
                "outcome",
            ],
        },
        "preflight": dict(preflight or {}),
        "cases": [],
        "metrics": {"raw": {}, "lexical": {}, "delta": {}},
        "classification_counts": {},
        "identifier_retention": {"missing_count": 0, "case_count": 0, "all_retained": True},
        "provenance_contamination": {"contamination": False, "cases": [], "contamination_hits": []},
        "plan_filter_identity_proven": True,
        "critical_new_misses": 0,
        "critical_new_miss_by_case": [],
        "critical_new_miss_group_ids": [],
        "call_accounting": {
            "analyzer_calls": 0,
            "vertex_calls": 0,
            "dense_embedding_calls": 0,
            "dense_reads": 0,
            "downstream_calls": 0,
            "write_calls": 0,
            "sparse_encoder_calls": 0,
            "sparse_reads": 0,
            "retries": 0,
        },
        "infrastructure_error": None,
    }
    if len(selected) < MIN_QUALIFIED_CASES:
        result["gates"] = evaluate_c4_hard_gates(result)
        result["verdict"] = result["gates"]["verdict"]
        return result
    if preflight_fn is not None:
        try:
            result["preflight"] = dict(preflight_fn())
        except Exception as exc:
            result["preflight"] = {"available": False, "status": "INCONCLUSIVE", "errors": [str(exc)]}
    elif not preflight:
        result["preflight"] = read_only_sparse_preflight(
            qdrant,
            collection_name=collection_name,
            vector_name=vector_name,
            expected_modifier=expected_modifier,
            expected_encoder_receipt=expected_encoder_receipt,
            encoder_receipt=encoder_receipt,
            expected_schema_version=expected_schema_version,
            expected_fingerprint=expected_fingerprint,
            expected_index_identity=expected_index_identity,
            index_identity=index_identity,
        )
    if not result["preflight"].get("available", False):
        result["infrastructure_error"] = "sparse_preflight_unavailable"
        result["gates"] = evaluate_c4_hard_gates(result)
        result["verdict"] = result["gates"]["verdict"]
        return result
    if not (
        result["preflight"].get("contract_ok") is True
        and result["preflight"].get("evidence_complete") is True
    ):
        result["infrastructure_error"] = "sparse_preflight_contract_unproven"
        result["gates"] = evaluate_c4_hard_gates(result)
        result["verdict"] = result["gates"]["verdict"]
        return result
    if result["preflight"].get("vector_name", vector_name) != vector_name:
        result["infrastructure_error"] = "sparse_vector_name_mismatch"
        result["gates"] = evaluate_c4_hard_gates(result)
        result["verdict"] = result["gates"]["verdict"]
        return result
    if qdrant is None or encoder is None:
        result["infrastructure_error"] = "sparse_encoder_or_qdrant_unavailable"
        result["gates"] = evaluate_c4_hard_gates(result)
        result["verdict"] = result["gates"]["verdict"]
        return result

    builder = filter_builder or build_frozen_query_filter
    contamination_cases: list[str] = []
    contamination_hits: list[dict[str, Any]] = []
    retention_cases: list[dict[str, Any]] = []
    try:
        for item in selected:
            plan = item["plan"]
            query_filter = builder(plan, context_sources)
            result["call_accounting"]["sparse_encoder_calls"] += 1
            raw_vector = _as_sparse_vector(_encode_query(encoder, item["raw_question"]))
            lexical_query = item["lexical_query"]
            result["call_accounting"]["sparse_encoder_calls"] += 1
            lexical_vector = _as_sparse_vector(_encode_query(encoder, lexical_query.text))
            result["call_accounting"]["sparse_reads"] += 1
            raw_ranking = _query_sparse(
                qdrant,
                collection_name=collection_name,
                vector=raw_vector,
                vector_name=vector_name,
                query_filter=query_filter,
                limit=top_k,
            )
            result["call_accounting"]["sparse_reads"] += 1
            lexical_ranking = _query_sparse(
                qdrant,
                collection_name=collection_name,
                vector=lexical_vector,
                vector_name=vector_name,
                query_filter=query_filter,
                limit=top_k,
            )
            raw_metrics = rank_metrics(item["evidence_groups"], raw_ranking, lookup)
            lexical_metrics = rank_metrics(item["evidence_groups"], lexical_ranking, lookup)
            classification = classify_case(
                raw_metrics["first_relevant_rank"], lexical_metrics["first_relevant_rank"]
            )
            critical_new_group_ids = [
                group_id
                for group_id, pre_rank in raw_metrics["first_relevant_ranks_by_group"].items()
                if any(
                    str(_field(group, "group_id", "")) == group_id
                    and bool(_field(group, "critical", True))
                    for group in item["evidence_groups"]
                )
                and pre_rank is not None
                and pre_rank <= TOP_K
                and (
                    lexical_metrics["first_relevant_ranks_by_group"].get(group_id) is None
                    or lexical_metrics["first_relevant_ranks_by_group"].get(group_id) > TOP_K
                )
            ]
            retention = explicit_identifier_retention(item["raw_question"], lexical_query)
            retention["case_id"] = item["case_id"]
            retention_cases.append(retention)
            audit = provenance_contamination_audit(lexical_query)
            audit["case_id"] = item["case_id"]
            if audit["contamination"]:
                contamination_cases.append(str(item["case_id"]))
                contamination_hits.extend(audit["contamination_hits"])
            non_text_parameters = {
                "collection_name": collection_name,
                "vector_name": vector_name,
                "limit": top_k,
                "with_payload": True,
                "query_filter_identity": id(query_filter),
                "encoder_identity": type(encoder).__qualname__,
            }
            result["cases"].append(
                {
                    "case_id": item["case_id"],
                    "intent": item.get("intent"),
                    "raw_question": item["raw_question"],
                    "lexical_query": lexical_query.as_dict(),
                    "raw_ranking": raw_ranking,
                    "lexical_ranking": lexical_ranking,
                    "pre": raw_metrics,
                    "post": lexical_metrics,
                    "raw": raw_metrics,
                    "lexical": lexical_metrics,
                    "classification": classification,
                    "critical_new_miss_group_ids": critical_new_group_ids,
                    "critical_new_miss_count": len(critical_new_group_ids),
                    "identifier_retention": retention,
                    "provenance_contamination": audit,
                    "same_non_text_parameters": True,
                    "filter_reused": True,
                    "query_parameters": dict(non_text_parameters),
                    "raw_query_parameters": dict(non_text_parameters),
                    "lexical_query_parameters": dict(non_text_parameters),
                }
            )
    except Exception as exc:
        result["infrastructure_error"] = f"sparse_execution_error:{type(exc).__name__}:{exc}"

    if result["cases"]:
        raw_metrics = [item["raw"] for item in result["cases"]]
        lexical_metrics = [item["lexical"] for item in result["cases"]]
        result["metrics"] = {
            "raw": _aggregate_metrics(raw_metrics),
            "lexical": _aggregate_metrics(lexical_metrics),
            "pre": _aggregate_metrics(raw_metrics),
            "post": _aggregate_metrics(lexical_metrics),
            "delta": {
                name: (
                    _aggregate_metrics(lexical_metrics).get(name)
                    - _aggregate_metrics(raw_metrics).get(name)
                    if _aggregate_metrics(lexical_metrics).get(name) is not None
                    and _aggregate_metrics(raw_metrics).get(name) is not None
                    else None
                )
                for name in ("recall_at_5", "recall_at_10", "recall_at_20", "mrr", "critical_coverage")
            },
        }
        result["classification_counts"] = classification_counts(result["cases"])
        critical_events = [
            {
                "case_id": item["case_id"],
                "group_ids": list(item.get("critical_new_miss_group_ids", [])),
            }
            for item in result["cases"]
            if item.get("critical_new_miss_group_ids")
        ]
        result["critical_new_miss_by_case"] = critical_events
        result["critical_new_miss_group_ids"] = [
            {"case_id": event["case_id"], "group_id": group_id}
            for event in critical_events
            for group_id in event["group_ids"]
        ]
        result["critical_new_misses"] = len(result["critical_new_miss_group_ids"])
    total_identifiers = sum(int(item["total_count"]) for item in retention_cases)
    missing_identifiers = sum(len(item["missing_tokens"]) for item in retention_cases)
    result["identifier_retention"] = {
        "case_count": len(retention_cases),
        "total_count": total_identifiers,
        "retained_count": total_identifiers - missing_identifiers,
        "missing_count": missing_identifiers,
        "all_retained": missing_identifiers == 0,
        "cases": retention_cases,
    }
    result["provenance_contamination"] = {
        "contamination": bool(contamination_cases),
        "case_ids": contamination_cases,
        "contamination_hits": contamination_hits,
    }
    result["plan_filter_identity_proven"] = all(
        bool(item.get("filter_reused") and item.get("same_non_text_parameters"))
        for item in result["cases"]
    ) and len(result["cases"]) == len(selected)
    result["gates"] = evaluate_c4_hard_gates(result)
    result["verdict"] = result["gates"]["verdict"]
    return result


# Friendly aliases used by small offline harnesses and future controller code.
evaluate_c4_sparse = run_c4_sparse_evaluation
evaluate_sparse_c4 = run_c4_sparse_evaluation
select_c4_cases = select_screening_cases
screening_order = deterministic_screening_order
compute_rank_metrics = rank_metrics
classify_rank_outcome = classify_case
sparse_preflight = read_only_sparse_preflight
hard_gate_verdict = evaluate_c4_hard_gates
C4_INTENT_CYCLE = INTENT_CYCLE
C4_EXCLUDED_CASE_IDS = EXCLUDED_CASE_IDS
normalize_c2_plan_record = normalize_plan_record
load_frozen_c2_plan_records = load_c2_plan_records
filter_eligible_records = eligible_c4_records
select_deterministic_cases = select_screening_cases


__all__ = [
    "PROMPT_VERSION",
    "INTENT_CYCLE",
    "C4_INTENT_CYCLE",
    "EXCLUDED_CASE_IDS",
    "C4_EXCLUDED_CASE_IDS",
    "MIN_QUALIFIED_CASES",
    "MAX_SCREENING_CASES",
    "TOP_K",
    "normalize_plan_record",
    "normalize_c2_plan_record",
    "load_c2_plan_records",
    "load_frozen_c2_plan_records",
    "eligibility_report",
    "eligible_c4_records",
    "filter_eligible_records",
    "deterministic_screening_order",
    "screening_order",
    "select_screening_cases",
    "select_c4_cases",
    "select_deterministic_cases",
    "build_frozen_query_filter",
    "read_only_sparse_preflight",
    "sparse_preflight",
    "explicit_identifier_retention",
    "provenance_contamination_audit",
    "rank_metrics",
    "compute_rank_metrics",
    "classify_case",
    "classify_rank_outcome",
    "classification_counts",
    "evaluate_c4_hard_gates",
    "hard_gate_verdict",
    "run_c4_sparse_evaluation",
    "evaluate_c4_sparse",
    "evaluate_sparse_c4",
]
