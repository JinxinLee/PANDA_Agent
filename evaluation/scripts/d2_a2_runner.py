"""D2-A2 frozen-case terminology runner.

Runs the preregistered D2-A2 terminology/paraphrase case artifact against the
deterministic D1-compatible evaluation state (``d2_a2_state``) and the FROZEN
D2 shadow resolver (``EntityResolver.resolve_shadow``).  The runner consumes
cases; it never authors them.  It never modifies resolver code, never calls a
model/Vertex/network/DB/Qdrant, and records resolver failures instead of
repairing them.

Case schema (consumed; authored by the D2-A2 coordinator):

    cases:
      - case_id: C01
        category: <string>
        question: <string>
        plan:
          target_repositories: [...]
          resolved_versions: {repo: version}     # optional
          analyzer_concepts:                      # optional; each support span
            - value: ...                         # must be a substring of the
              support_spans: [...]               # case question
        expected_status: RESOLVED_UNIQUE|AMBIGUOUS|UNRESOLVED|REJECTED_VERSION|REJECTED_SCOPE
        expected_object_ids: [...]               # matched object(s); [] for abstain/ambiguous
        expected_canonical_object_ids: [...]     # [] means canonical_object_id must be None
        expected_resolution_kind: true_identity|structural|descriptive_inferential|corrective|none
        expected_evidence_tier: G|S|D|corrective|none
        source_evidence: <string>
        source_ids: [...]
        source_version_ids: [...]
        applicability: AVAILABLE|NOT_APPLICABLE
        notes: <string>
    not_applicable:
      - category: ...
        reason: ...

Comparison semantics (frozen): a case is correct iff SOME receipt resolution
satisfies the expected status + identity targets + canonical expectation AND
every recorded negative expectation holds.  Negative expectations come only
from the case's own fields: ``expected_canonical_object_ids == []`` requires
``canonical_object_id is None`` on the satisfying resolution, and an
abstain/ambiguous ``expected_status`` requires no confident
``RESOLVED_UNIQUE`` resolution anywhere in the receipt (the conservative
whole-question fallback mention targets the same question).  Positive
RESOLVED_UNIQUE cases record no receipt-wide negative expectation, so an
extra co-resolution is recorded for audit but does not fail the case.  A
resolution achieved through a different evidence tier than the expected one
is an EVIDENCE_AUTHORITY_VIOLATION (recorded, never hidden).  Every
non-correct applicable case carries exactly one primary failure type from the
preregistered taxonomy.

CLI:
    PYTHONPATH=src python evaluation/scripts/d2_a2_runner.py \
        --project-root . \
        --cases data/evaluation/d2_a2_terminology_cases.yaml \
        --results data/evaluation/results/d2_a2_results.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from panda_agent.entity_resolution import (
    AMBIGUOUS,
    REJECTED_SCOPE,
    REJECTED_VERSION,
    RESOLVED_UNIQUE,
    UNRESOLVED,
    EntityResolver,
)

from d2_a2_state import D2EvalState, build_evaluation_state, validate_evaluation_state

# Repo HEAD when the D2-A2 evaluation infrastructure was authored (task brief).
BASELINE_COMMIT = "67eff2b"
STATE_TYPE = "deterministic_in_memory_d1_compatible"

RESOLVED_STATUSES = frozenset({RESOLVED_UNIQUE})
ABSTAIN_STATUSES = frozenset({UNRESOLVED, REJECTED_VERSION, REJECTED_SCOPE})
EXPECTED_STATUSES = frozenset({RESOLVED_UNIQUE, AMBIGUOUS, UNRESOLVED, REJECTED_VERSION, REJECTED_SCOPE})
EXPECTED_KINDS = frozenset(
    {"true_identity", "structural", "descriptive_inferential", "corrective", "none"}
)
EXPECTED_TIERS = frozenset({"G", "S", "D", "corrective", "none"})
APPLICABILITY_VALUES = frozenset({"AVAILABLE", "NOT_APPLICABLE"})

# Failure taxonomy (D2-A2 preregistration); every non-correct applicable case
# carries exactly one primary type.
MENTION_EXTRACTION_FAILURE = "MENTION_EXTRACTION_FAILURE"
QUERY_GROUNDING_FAILURE = "QUERY_GROUNDING_FAILURE"
CANDIDATE_GENERATION_FAILURE = "CANDIDATE_GENERATION_FAILURE"
INSUFFICIENT_DESCRIPTIVE_FEATURES = "INSUFFICIENT_DESCRIPTIVE_FEATURES"
COMPETITION_AMBIGUITY = "COMPETITION_AMBIGUITY"
WRONG_CONFIDENT_RESOLUTION = "WRONG_CONFIDENT_RESOLUTION"
FALSE_CANONICALIZATION = "FALSE_CANONICALIZATION"
VERSION_SCOPE_FAILURE = "VERSION_SCOPE_FAILURE"
CORRECTIVE_TERM_FAILURE = "CORRECTIVE_TERM_FAILURE"
EVIDENCE_AUTHORITY_VIOLATION = "EVIDENCE_AUTHORITY_VIOLATION"
MISSING_STRUCTURED_STATE = "MISSING_STRUCTURED_STATE"
CASE_INVALID = "CASE_INVALID"
NOT_APPLICABLE = "NOT_APPLICABLE"

DECISION_BUCKETS = (
    "correct_resolve",
    "wrong_resolve",
    "correct_abstain",
    "wrong_abstain",
    "correct_ambiguous",
    "wrong_ambiguous",
    "not_applicable",
)


def _normalization_key(value: str) -> str:
    return " ".join(value.casefold().split())


def _git_head(project_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip()
    except Exception:
        return "unknown"


def _safe_div(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


# ---------------------------------------------------------------------------
# Case schema validation
# ---------------------------------------------------------------------------


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _case_schema_problems(case: Any, state_ids: frozenset[str]) -> list[str]:
    """Return the list of schema violations (empty means the case is valid).

    Expected IDs are never checked against the plan here; they are checked
    against the STATE only at classification time (MISSING_STRUCTURED_STATE).
    """

    if not isinstance(case, dict):
        return ["case is not a mapping"]
    problems: list[str] = []
    for key in (
        "case_id",
        "category",
        "question",
        "expected_status",
        "expected_resolution_kind",
        "expected_evidence_tier",
        "applicability",
    ):
        if not isinstance(case.get(key), str) or not case.get(key):
            problems.append(f"missing or empty string field {key!r}")
    if problems:
        return problems
    if case["question"].strip() != case["question"] or not case["question"].strip():
        problems.append("question must be stripped and non-empty")
    if case["expected_status"] not in EXPECTED_STATUSES:
        problems.append(f"unknown expected_status {case['expected_status']!r}")
    if case["expected_resolution_kind"] not in EXPECTED_KINDS:
        problems.append(f"unknown expected_resolution_kind {case['expected_resolution_kind']!r}")
    if case["expected_evidence_tier"] not in EXPECTED_TIERS:
        problems.append(f"unknown expected_evidence_tier {case['expected_evidence_tier']!r}")
    if case["applicability"] not in APPLICABILITY_VALUES:
        problems.append(f"unknown applicability {case['applicability']!r}")
    if not _string_list(case.get("expected_object_ids", [])):
        problems.append("expected_object_ids must be a list of strings")
    if not _string_list(case.get("expected_canonical_object_ids", [])):
        problems.append("expected_canonical_object_ids must be a list of strings")
    if (
        case["expected_status"] == RESOLVED_UNIQUE
        and isinstance(case.get("expected_object_ids"), list)
        and not case["expected_object_ids"]
    ):
        problems.append("RESOLVED_UNIQUE cases must name expected_object_ids")

    plan = case.get("plan")
    if not isinstance(plan, dict):
        problems.append("plan must be a mapping")
        return problems
    if not _string_list(plan.get("target_repositories") or []):
        problems.append("plan.target_repositories must be a list of strings")
    resolved_versions = plan.get("resolved_versions")
    if resolved_versions is not None:
        if not isinstance(resolved_versions, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in resolved_versions.items()
        ):
            problems.append("plan.resolved_versions must map repo names to versions")
    analyzer_concepts = plan.get("analyzer_concepts")
    if analyzer_concepts is not None:
        if not isinstance(analyzer_concepts, list):
            problems.append("plan.analyzer_concepts must be a list")
            return problems
        question = case["question"]
        for index, item in enumerate(analyzer_concepts):
            if not isinstance(item, dict):
                problems.append(f"analyzer_concepts[{index}] is not a mapping")
                continue
            value = item.get("value")
            spans = item.get("support_spans")
            if not isinstance(value, str) or not value.strip():
                problems.append(f"analyzer_concepts[{index}].value must be a non-empty string")
                continue
            if not _string_list(spans) or not spans:
                problems.append(
                    f"analyzer_concepts[{index}].support_spans must be a non-empty list of strings"
                )
                continue
            for span in spans:
                if span not in question:
                    problems.append(
                        f"analyzer_concepts[{index}] support span {span!r} is not a "
                        "substring of the case question"
                    )
    return problems


def _build_plan(case: dict[str, Any]) -> dict[str, Any]:
    """Deterministic resolver plan; expected IDs are structurally excluded."""

    plan_config = case.get("plan") or {}
    concepts: list[dict[str, Any]] = []
    for item in plan_config.get("analyzer_concepts") or []:
        concepts.append(
            {"value": item["value"], "support_spans": list(item["support_spans"])}
        )
    return {
        "intent": "terminology_resolution",
        "target_repositories": list(plan_config.get("target_repositories") or []),
        "resolved_versions": dict(plan_config.get("resolved_versions") or {}),
        "resolved_aliases": {},
        "symbols": [],
        # Flat plan.concepts is deliberately never populated: flattened
        # concepts are not authoritative mention evidence (D2-A1R1 repair 1).
        "concepts": [],
        "analysis_diagnostics": {
            "analyzer_accepted_semantic_delta": {"symbols": [], "concepts": concepts}
        },
    }


# ---------------------------------------------------------------------------
# Comparison semantics
# ---------------------------------------------------------------------------


def _candidate_ids(resolution: Any) -> set[str]:
    return {
        str(item.get("object_id", ""))
        for item in resolution.candidates
        if item.get("object_id")
    }


def _status_target_match(
    resolution: Any,
    expected_status: str,
    expected_object_ids: set[str],
) -> bool:
    if resolution.status != expected_status:
        return False
    if expected_status == RESOLVED_UNIQUE:
        return bool(expected_object_ids) and resolution.matched_object_id in expected_object_ids
    if expected_status in {REJECTED_VERSION, REJECTED_SCOPE}:
        return not expected_object_ids or bool(_candidate_ids(resolution) & expected_object_ids)
    # AMBIGUOUS / UNRESOLVED never select an object.
    return resolution.matched_object_id is None


def _canonical_match(resolution: Any, expected_canonical_ids: set[str]) -> bool:
    if expected_canonical_ids:
        if resolution.canonical_object_id in expected_canonical_ids:
            return True
        # D2-A1R2 comparator clarification: a Tier S/Direct match on the
        # canonical record itself carries canonical_object_id = None (no
        # cross-record canonicalization occurred).  That satisfies the
        # canonical expectation; only a different canonical target or a
        # confidently canonicalized non-expected record fails.
        return (
            resolution.canonical_object_id is None
            and resolution.matched_object_id in expected_canonical_ids
        )
    return resolution.canonical_object_id is None


def _evidence_check(
    resolution: Any, expected_kind: str, expected_tier: str
) -> tuple[bool, str | None]:
    tiers = {item.tier for item in resolution.evidence}
    if expected_tier != "none" and expected_tier not in tiers:
        return False, (
            f"expected evidence tier {expected_tier!r} absent; observed {sorted(tiers)}"
        )
    if expected_kind == "true_identity":
        ok = "G" in tiers
    elif expected_kind == "structural":
        ok = "S" in tiers and (
            resolution.canonical_object_id is None
            or (
                "G" in tiers
                and resolution.diagnostics.get("canonicalization") is True
            )
        )
    elif expected_kind == "descriptive_inferential":
        ok = "D" in tiers and resolution.diagnostics.get("descriptive_inference") is True
    elif expected_kind == "corrective":
        ok = (
            resolution.diagnostics.get("corrective") is True
            and resolution.diagnostics.get("identity_authority") is False
        )
    else:
        ok = True
    if not ok:
        observed = ", ".join(
            f"{key}={resolution.diagnostics.get(key)}"
            for key in (
                "canonicalization",
                "descriptive_inference",
                "corrective",
                "identity_authority",
            )
        )
        return False, (
            f"evidence-authority mismatch for kind {expected_kind!r} "
            f"(tiers={sorted(tiers)}; {observed})"
        )
    return True, None


def _negative_violation(
    resolutions: list[Any],
    expected_status: str,
) -> str | None:
    """Cross-resolution negative-expectation check.

    A case only records negative expectations through its expected fields:
    ``expected_canonical_object_ids == []`` records "canonical_object_id must
    be None" and is enforced on the satisfying resolution itself (see
    ``_canonical_match``); an abstain/ambiguous ``expected_status`` records
    "no single identity may be selected", which applies to the whole receipt
    because the conservative whole-question fallback mention targets the same
    question.  Positive RESOLVED_UNIQUE cases record no receipt-wide negative
    expectation, so an extra resolution (e.g. a co-resolving fallback for an
    unresolved side token) is audit-recorded but does not fail the case.
    """

    if expected_status == RESOLVED_UNIQUE:
        return None
    for index, resolution in enumerate(resolutions):
        if resolution.status == RESOLVED_UNIQUE and resolution.matched_object_id:
            return (
                f"resolution {resolution.mention_text!r} confidently resolved "
                f"{resolution.matched_object_id} in a case expecting {expected_status}"
            )
    return None


def _decision_bucket(
    expected_status: str,
    correct: bool,
    has_confident_resolve: bool,
    has_ambiguous: bool,
) -> str:
    if correct:
        if expected_status == RESOLVED_UNIQUE:
            return "correct_resolve"
        if expected_status == AMBIGUOUS:
            return "correct_ambiguous"
        return "correct_abstain"
    if expected_status == RESOLVED_UNIQUE:
        return "wrong_resolve" if has_confident_resolve else "wrong_abstain"
    if expected_status == AMBIGUOUS:
        return "wrong_resolve" if has_confident_resolve else "wrong_ambiguous"
    if has_confident_resolve:
        return "wrong_resolve"
    if has_ambiguous:
        return "wrong_ambiguous"
    return "wrong_abstain"


def _classify_failure(
    *,
    expected_status: str,
    expected_kind: str,
    expected_object_ids: set[str],
    expected_all_ids: set[str],
    state_ids: frozenset[str],
    resolutions: list[Any],
    status_target_satisfying: set[int],
    satisfying: set[int],
    evidence_valid: bool | None,
    false_canonicalization: bool,
    has_confident_resolve: bool,
    concept_keys: set[str],
) -> str:
    missing = sorted(expected_all_ids - state_ids)
    if missing:
        return MISSING_STRUCTURED_STATE
    if not resolutions:
        return MENTION_EXTRACTION_FAILURE
    if satisfying:
        if evidence_valid is False:
            return EVIDENCE_AUTHORITY_VIOLATION
        return WRONG_CONFIDENT_RESOLUTION
    if status_target_satisfying and false_canonicalization:
        return FALSE_CANONICALIZATION
    if expected_kind == "corrective":
        if not any(
            resolution.diagnostics.get("corrective") is True for resolution in resolutions
        ):
            return CORRECTIVE_TERM_FAILURE
        return WRONG_CONFIDENT_RESOLUTION if has_confident_resolve else CORRECTIVE_TERM_FAILURE
    if expected_status == RESOLVED_UNIQUE:
        for resolution in resolutions:
            if expected_object_ids & _candidate_ids(resolution):
                if resolution.status == AMBIGUOUS:
                    return COMPETITION_AMBIGUITY
                if resolution.status in {REJECTED_VERSION, REJECTED_SCOPE}:
                    return VERSION_SCOPE_FAILURE
                if resolution.status == RESOLVED_UNIQUE:
                    return WRONG_CONFIDENT_RESOLUTION
        if has_confident_resolve:
            return WRONG_CONFIDENT_RESOLUTION
        if expected_kind == "descriptive_inferential":
            has_descriptive = any(
                resolution.mention_kind == "descriptive" for resolution in resolutions
            )
            if not has_descriptive:
                concept_mentioned = any(
                    _normalization_key(resolution.mention_text) in concept_keys
                    for resolution in resolutions
                )
                return QUERY_GROUNDING_FAILURE if not concept_mentioned else MENTION_EXTRACTION_FAILURE
            descriptive = [
                resolution
                for resolution in resolutions
                if resolution.mention_kind == "descriptive"
            ]
            if any(resolution.candidates for resolution in descriptive):
                return INSUFFICIENT_DESCRIPTIVE_FEATURES
            return CANDIDATE_GENERATION_FAILURE
        return CANDIDATE_GENERATION_FAILURE
    if expected_status == AMBIGUOUS:
        if has_confident_resolve:
            return WRONG_CONFIDENT_RESOLUTION
        return CANDIDATE_GENERATION_FAILURE
    # Abstention expected (UNRESOLVED / REJECTED_*).
    if has_confident_resolve:
        return WRONG_CONFIDENT_RESOLUTION
    if any(resolution.status == AMBIGUOUS for resolution in resolutions):
        return COMPETITION_AMBIGUITY
    if expected_status in {REJECTED_VERSION, REJECTED_SCOPE}:
        return VERSION_SCOPE_FAILURE
    if any(
        resolution.status in {REJECTED_VERSION, REJECTED_SCOPE}
        for resolution in resolutions
    ):
        return VERSION_SCOPE_FAILURE
    return CANDIDATE_GENERATION_FAILURE


# ---------------------------------------------------------------------------
# Per-case evaluation
# ---------------------------------------------------------------------------


def evaluate_case(
    case: dict[str, Any],
    state: D2EvalState,
    state_ids: frozenset[str],
    resolver: EntityResolver,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "case_id": case.get("case_id") if isinstance(case, dict) else None,
        "category": case.get("category") if isinstance(case, dict) else None,
        "question": case.get("question") if isinstance(case, dict) else None,
        "expected_status": case.get("expected_status") if isinstance(case, dict) else None,
        "expected_object_ids": case.get("expected_object_ids") if isinstance(case, dict) else [],
        "expected_canonical_object_ids": case.get("expected_canonical_object_ids")
        if isinstance(case, dict)
        else [],
        "expected_resolution_kind": case.get("expected_resolution_kind")
        if isinstance(case, dict)
        else None,
        "expected_evidence_tier": case.get("expected_evidence_tier")
        if isinstance(case, dict)
        else None,
        "applicability": case.get("applicability") if isinstance(case, dict) else None,
        "not_applicable": False,
        "case_invalid": False,
        "correct": None,
        "decision": None,
        "primary_failure_type": None,
        "failure_detail": None,
        "evidence_valid": None,
        "has_confident_resolve": False,
        "has_ambiguous": False,
        "plan": None,
        "actual": None,
    }

    if record["applicability"] == "NOT_APPLICABLE":
        record["not_applicable"] = True
        record["decision"] = "not_applicable"
        record["primary_failure_type"] = NOT_APPLICABLE
        return record
    if case.get("invalid") is True:
        # D2-A2 §10: a case proven objectively invalid after execution is
        # recorded INVALID_CASE with its reason and excluded from metrics;
        # it is never silently replaced.
        record["case_invalid"] = True
        record["correct"] = False
        record["decision"] = "not_applicable"
        record["primary_failure_type"] = CASE_INVALID
        record["failure_detail"] = str(case.get("invalid_reason") or "invalid case")
        return record

    problems = _case_schema_problems(case, state_ids)
    if problems:
        record["case_invalid"] = True
        record["correct"] = False
        record["decision"] = "not_applicable"
        record["primary_failure_type"] = CASE_INVALID
        record["failure_detail"] = "; ".join(problems)
        return record

    expected_status = case["expected_status"]
    expected_kind = case["expected_resolution_kind"]
    expected_tier = case["expected_evidence_tier"]
    expected_object_ids = set(case["expected_object_ids"])
    expected_canonical_ids = set(case["expected_canonical_object_ids"])
    expected_all_ids = expected_object_ids | expected_canonical_ids
    concept_keys = {
        _normalization_key(item["value"])
        for item in (case.get("plan") or {}).get("analyzer_concepts") or []
    }

    plan = _build_plan(case)
    record["plan"] = plan
    try:
        receipt = resolver.resolve_shadow(case["question"], plan)
    except Exception as exc:  # frozen resolver: record, never repair
        record["correct"] = False
        record["decision"] = _decision_bucket(expected_status, False, False, False)
        record["primary_failure_type"] = MISSING_STRUCTURED_STATE
        record["failure_detail"] = (
            f"resolve_shadow raised {type(exc).__name__}: {exc}"
        )
        return record

    resolutions = list(receipt.resolutions)
    record["has_confident_resolve"] = any(
        resolution.status == RESOLVED_UNIQUE and resolution.matched_object_id
        for resolution in resolutions
    )
    record["has_ambiguous"] = any(
        resolution.status == AMBIGUOUS for resolution in resolutions
    )
    record["actual"] = {
        "receipt": receipt.as_dict(),
        "statuses": [resolution.status for resolution in resolutions],
    }

    status_target_satisfying = {
        index
        for index, resolution in enumerate(resolutions)
        if _status_target_match(resolution, expected_status, expected_object_ids)
    }
    satisfying = {
        index
        for index in status_target_satisfying
        if _canonical_match(resolutions[index], expected_canonical_ids)
    }
    false_canonicalization = bool(status_target_satisfying) and not satisfying

    # Evidence validity is evaluable only where evidence can exist: resolved
    # outcomes for the tier-checking kinds, plus corrective diagnostics on the
    # corrective (abstain-kind) outcome.  Abstain/ambiguous outcomes carry no
    # tier evidence and are excluded from the evidence-validity denominator.
    evidence_evaluable = bool(satisfying) and (
        expected_kind == "corrective"
        or (expected_status == RESOLVED_UNIQUE and expected_kind != "none")
    )
    evidence_valid: bool | None = None
    evidence_details: list[str] = []
    if evidence_evaluable:
        evidence_valid = True
        for index in sorted(satisfying):
            ok, detail = _evidence_check(
                resolutions[index], expected_kind, expected_tier
            )
            evidence_valid = evidence_valid and ok
            if not ok and detail:
                evidence_details.append(detail)

    negative_detail = _negative_violation(resolutions, expected_status)
    correct = (
        bool(satisfying)
        and evidence_valid is not False
        and negative_detail is None
    )

    record["correct"] = correct
    record["evidence_valid"] = evidence_valid
    record["decision"] = _decision_bucket(
        expected_status,
        correct,
        record["has_confident_resolve"],
        record["has_ambiguous"],
    )
    if not correct:
        record["primary_failure_type"] = _classify_failure(
            expected_status=expected_status,
            expected_kind=expected_kind,
            expected_object_ids=expected_object_ids,
            expected_all_ids=expected_all_ids,
            state_ids=state_ids,
            resolutions=resolutions,
            status_target_satisfying=status_target_satisfying,
            satisfying=satisfying,
            evidence_valid=evidence_valid,
            false_canonicalization=false_canonicalization,
            has_confident_resolve=record["has_confident_resolve"],
            concept_keys=concept_keys,
        )
        details = []
        if false_canonicalization:
            details.append(
                "canonical_object_id expectation violated on the status/target-matching resolution"
            )
        details.extend(evidence_details)
        if negative_detail:
            details.append(negative_detail)
        if not details:
            details.append(
                f"no resolution satisfied expected status {expected_status} with the "
                "expected identity targets"
            )
        record["failure_detail"] = "; ".join(details)
    return record


# ---------------------------------------------------------------------------
# Metrics and reporting
# ---------------------------------------------------------------------------


def _compute_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    applicable = [
        record
        for record in records
        if not record["not_applicable"] and not record["case_invalid"]
    ]
    decisions = Counter(record["decision"] for record in records)
    accounting = {bucket: decisions.get(bucket, 0) for bucket in DECISION_BUCKETS}

    resolve_cases = [
        record for record in applicable if record["expected_status"] == RESOLVED_UNIQUE
    ]
    canonical_expected = [
        record for record in applicable if record["expected_canonical_object_ids"]
    ]
    canonical_none_expected = [
        record
        for record in applicable
        if not record["expected_canonical_object_ids"]
        and record["expected_status"] == RESOLVED_UNIQUE
    ]
    abstain_cases = [
        record for record in applicable if record["expected_status"] in ABSTAIN_STATUSES
    ]
    ambiguous_cases = [
        record for record in applicable if record["expected_status"] == AMBIGUOUS
    ]
    negative_cases = [
        record for record in applicable if record["expected_status"] != RESOLVED_UNIQUE
    ]
    evidence_checked = [
        record
        for record in applicable
        if record["expected_resolution_kind"] != "none"
        and record["evidence_valid"] is not None
    ]

    corrective_cases = [
        record
        for record in applicable
        if record["expected_resolution_kind"] == "corrective"
    ]

    return {
        "case_count": len(records),
        "applicable_case_count": len(applicable),
        "case_invalid_count": sum(1 for record in records if record["case_invalid"]),
        "not_applicable_case_count": sum(
            1 for record in records if record["not_applicable"]
        ),
        "correct_case_count": sum(1 for record in applicable if record["correct"]),
        "applicability": _safe_div(len(applicable), len(records)),
        "coverage": _safe_div(
            sum(1 for record in applicable if record["actual"]), len(applicable)
        ),
        "resolution_accuracy": _safe_div(
            sum(1 for record in resolve_cases if record["correct"]), len(resolve_cases)
        ),
        "canonicalization_accuracy_expected": _safe_div(
            sum(1 for record in canonical_expected if record["correct"]),
            len(canonical_expected),
        ),
        "canonicalization_accuracy_none_expected_source_native": _safe_div(
            sum(1 for record in canonical_none_expected if record["correct"]),
            len(canonical_none_expected),
        ),
        "abstention_accuracy": _safe_div(
            sum(1 for record in abstain_cases if record["correct"]), len(abstain_cases)
        ),
        "ambiguity_accuracy": _safe_div(
            sum(1 for record in ambiguous_cases if record["correct"]),
            len(ambiguous_cases),
        ),
        "false_positive_resolution_rate": _safe_div(
            sum(1 for record in negative_cases if record["has_confident_resolve"]),
            len(negative_cases),
        ),
        "evidence_validity": _safe_div(
            sum(1 for record in evidence_checked if record["evidence_valid"] is True),
            len(evidence_checked),
        ),
        "corrective_handling_correct": sum(
            1 for record in corrective_cases if record["correct"]
        ),
        "corrective_handling_incorrect": sum(
            1 for record in corrective_cases if not record["correct"]
        ),
        "decision_accounting": accounting,
    }


def _category_summaries(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_category.setdefault(str(record["category"]), []).append(record)
    summaries: dict[str, Any] = {}
    for category in sorted(by_category):
        group = by_category[category]
        applicable = [
            record
            for record in group
            if not record["not_applicable"] and not record["case_invalid"]
        ]
        negative = [
            record for record in applicable if record["expected_status"] != RESOLVED_UNIQUE
        ]
        summaries[category] = {
            "cases": len(group),
            "applicable": len(applicable),
            "correct": sum(1 for record in applicable if record["correct"]),
            "incorrect": sum(1 for record in applicable if record["correct"] is False),
            "not_applicable": sum(1 for record in group if record["not_applicable"]),
            "case_invalid": sum(1 for record in group if record["case_invalid"]),
            "false_positive_resolutions": sum(
                1 for record in negative if record["has_confident_resolve"]
            ),
            "decisions": dict(
                Counter(str(record["decision"]) for record in group)
            ),
            "failure_types": dict(
                Counter(
                    str(record["primary_failure_type"])
                    for record in group
                    if record["primary_failure_type"]
                )
            ),
        }
    return summaries


def _print_summary(
    state_report: dict[str, Any], metrics: dict[str, Any], records: list[dict[str, Any]]
) -> None:
    print("D2-A2 terminology evaluation summary")
    print(
        "state: valid={valid} objects={objects} accepted_relations={relations} "
        "accepted_aliases={aliases}".format(
            valid=state_report["valid"],
            objects=state_report["object_count"],
            relations=state_report["accepted_relation_count"],
            aliases=state_report["accepted_alias_count"],
        )
    )
    print(
        f"cases: total={metrics['case_count']} applicable={metrics['applicable_case_count']} "
        f"correct={metrics['correct_case_count']} "
        f"not_applicable={metrics['not_applicable_case_count']} "
        f"invalid={metrics['case_invalid_count']}"
    )
    accounting = metrics["decision_accounting"]
    print(
        "decision accounting: "
        + " ".join(f"{bucket}={accounting[bucket]}" for bucket in DECISION_BUCKETS)
    )
    print(
        f"corrective handling: correct={metrics['corrective_handling_correct']} "
        f"incorrect={metrics['corrective_handling_incorrect']}"
    )
    for name in (
        "resolution_accuracy",
        "canonicalization_accuracy_expected",
        "canonicalization_accuracy_none_expected_source_native",
        "abstention_accuracy",
        "ambiguity_accuracy",
        "false_positive_resolution_rate",
        "applicability",
        "coverage",
        "evidence_validity",
    ):
        print(f"{name}: {metrics[name]}")
    print("per-case results:")
    for record in records:
        statuses = record["actual"]["statuses"] if record["actual"] else []
        outcome = (
            "correct"
            if record["correct"]
            else ("not_applicable" if record["not_applicable"] else "incorrect")
        )
        suffix = (
            ""
            if record["correct"] or record["not_applicable"]
            else f" [{record['primary_failure_type']}]"
        )
        print(
            f"  {record['case_id']} ({record['category']}): "
            f"expected {record['expected_status']} actual {statuses} -> {outcome}{suffix}"
        )


def _load_cases(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"case artifact {path} must be a mapping")
    cases = payload.get("cases")
    not_applicable = payload.get("not_applicable") or []
    if not isinstance(cases, list):
        raise ValueError(f"case artifact {path} must contain a 'cases' list")
    if not isinstance(not_applicable, list):
        raise ValueError(f"case artifact {path}: 'not_applicable' must be a list")
    return cases, not_applicable


def run(
    project_root: Path,
    cases_path: Path,
    results_path: Path,
) -> dict[str, Any]:
    state = build_evaluation_state(project_root)
    state_report = validate_evaluation_state(state)
    if not state_report["valid"]:
        raise RuntimeError(
            f"evaluation-state validation gate failed: "
            f"{json.dumps(state_report, default=str)}"
        )
    resolver = EntityResolver(state.storage())
    state_ids = state.object_ids()

    cases, not_applicable_records = _load_cases(cases_path)
    records = [evaluate_case(case, state, state_ids, resolver) for case in cases]
    metrics = _compute_metrics(records)
    categories = _category_summaries(records)
    taxonomy = Counter(
        str(record["primary_failure_type"])
        for record in records
        if record["primary_failure_type"]
    )

    results: dict[str, Any] = {
        "run_provenance": {
            "head": _git_head(project_root),
            "baseline_commit": BASELINE_COMMIT,
            "case_artifact_path": str(cases_path),
            "state_type": STATE_TYPE,
            "state_valid": state_report["valid"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "case_count": len(cases),
        },
        "state_validation": state_report,
        "metrics": metrics,
        "failure_taxonomy_counts": dict(sorted(taxonomy.items())),
        "category_summaries": categories,
        "per_case_results": records,
        "not_applicable_records": not_applicable_records,
    }

    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    _print_summary(state_report, metrics, records)
    print(f"results written: {results_path}")
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--cases", required=True)
    parser.add_argument("--results", required=True)
    args = parser.parse_args(argv)
    run(Path(args.project_root), Path(args.cases), Path(args.results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
