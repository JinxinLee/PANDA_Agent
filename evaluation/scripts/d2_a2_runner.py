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
    RESOLVED_MULTIPLE,
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


def _confident_resolve_ids(resolutions: list[Any]) -> set[str]:
    """Object IDs confidently asserted by RESOLVED_UNIQUE/MULTIPLE decisions."""

    ids: set[str] = set()
    for resolution in resolutions:
        if resolution.status == RESOLVED_UNIQUE and resolution.matched_object_id:
            ids.add(str(resolution.matched_object_id))
        if resolution.status == RESOLVED_MULTIPLE:
            ids.update(
                str(item) for item in resolution.selected_object_ids
            )
    return ids


def _evaluate_isolation(
    resolutions: list[Any],
    isolation_tokens: dict[str, list[str]],
) -> tuple[bool | None, list[str]]:
    """Independent mention-isolation requirement (D2-A2R1 repair L).

    For each isolation key, the matching mention's descriptive evidence must
    exclude the other mentions' distinctive tokens.  Returns
    (valid | None when no isolation is declared, details).
    """

    if not isolation_tokens:
        return None, []
    details: list[str] = []
    valid = True
    for mention_text, forbidden_tokens in sorted(isolation_tokens.items()):
        for resolution in resolutions:
            if _normalization_key(resolution.mention_text) != _normalization_key(
                mention_text
            ):
                continue
            evidence_blob = " ".join(
                str(item.detail) for item in resolution.evidence
            ).lower()
            leaked = [
                token
                for token in forbidden_tokens
                if token.lower() in evidence_blob
            ]
            if leaked:
                valid = False
                details.append(
                    f"mention {mention_text!r} evidence leaked tokens {leaked}"
                )
    if not details:
        details.append("no cross-mention token leakage observed")
    return valid, details


def _classify_case_decision(
    *,
    expected_status: str,
    resolutions: list[Any],
    required_target_ids: set[str],
    expected_canonical_object_ids: set[str],
    allowed_context_object_ids: set[str],
    require_all_targets: bool,
    invalid: bool,
    isolation_tokens: dict[str, list[str]],
) -> dict[str, Any]:
    """D2-A2R2 repair A/E: target-scoped decision semantics.

    wrong_resolve   = a confident identity was asserted that is neither a
                      required primary target nor an explicitly allowed
                      contextual/co-mentioned identity;
    wrong_ambiguous = required primary target resolution failed because
                      ambiguity replaced it, with no prohibited confident
                      wrong identity;
    wrong_abstain   = required primary target resolution is
                      missing/unresolved/rejected with no prohibited
                      confident wrong identity and no ambiguity replacing it.

    Allowed contextual identities never satisfy a required primary target and
    never count as wrong confident identities.  Invalid cases return
    CASE_INVALID and are excluded from the authoritative valid-case
    accounting.
    """

    isolation_valid, _details = _evaluate_isolation(resolutions, isolation_tokens)
    confident_ids = _confident_resolve_ids(resolutions)
    confident_required = sorted(confident_ids & required_target_ids)
    confident_allowed = sorted(confident_ids & allowed_context_object_ids)
    confident_unexpected = sorted(
        confident_ids - required_target_ids - allowed_context_object_ids
    )
    has_confident = bool(confident_ids)
    has_ambiguous = any(resolution.status == AMBIGUOUS for resolution in resolutions)

    if invalid:
        return {
            "decision": "CASE_INVALID",
            "confident_required_target_ids": confident_required,
            "confident_allowed_context_ids": confident_allowed,
            "confident_unexpected_ids": confident_unexpected,
            "isolation_valid": isolation_valid,
        }

    if expected_status == RESOLVED_UNIQUE:
        if require_all_targets and required_target_ids:
            primary_satisfied = all(
                any(
                    _status_target_match(resolution, expected_status, {target_id})
                    and _canonical_match(resolution, {target_id})
                    for resolution in resolutions
                )
                for target_id in sorted(required_target_ids)
            )
        else:
            primary_satisfied = any(
                _status_target_match(resolution, expected_status, required_target_ids)
                and _canonical_match(resolution, expected_canonical_object_ids)
                for resolution in resolutions
            )
        correct = (
            primary_satisfied
            and isolation_valid is not False
            and not confident_unexpected
        )
        if correct:
            decision = "correct_resolve"
        elif confident_unexpected:
            decision = "wrong_resolve"
        elif has_ambiguous:
            decision = "wrong_ambiguous"
        else:
            decision = "wrong_abstain"
    elif expected_status == AMBIGUOUS:
        if has_confident:
            decision = "wrong_resolve"
        elif has_ambiguous:
            decision = "correct_ambiguous"
        else:
            decision = "wrong_ambiguous"
    else:
        # Abstention family: UNRESOLVED / REJECTED_VERSION / REJECTED_SCOPE,
        # and the corrective kind (which must never carry identity authority).
        if has_confident:
            decision = "wrong_resolve"
        elif expected_status == UNRESOLVED and any(
            resolution.status == UNRESOLVED for resolution in resolutions
        ):
            decision = "correct_abstain"
        elif expected_status in {REJECTED_VERSION, REJECTED_SCOPE} and any(
            resolution.status == expected_status for resolution in resolutions
        ):
            decision = "correct_abstain"
        else:
            decision = "wrong_abstain"

    return {
        "decision": decision,
        "confident_required_target_ids": confident_required,
        "confident_allowed_context_ids": confident_allowed,
        "confident_unexpected_ids": confident_unexpected,
        "isolation_valid": isolation_valid,
    }


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
        record["decision"] = "not_applicable"
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

    target_match_mode = str(case.get("target_match_mode") or ("ALL" if case.get("require_all_expected_targets") is True else "ANY"))
    require_all_targets = target_match_mode == "ALL" and len(expected_object_ids) > 1

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

    # D2-A2R1 repair D/L: multi-target ALL semantics and the independent
    # mention-isolation requirement.  For require-all cases every expected
    # target must be satisfied by some resolution; isolation cases must
    # additionally keep each mention's descriptive evidence free of the other
    # mentions' distinctive tokens.  Both requirements are recorded separately
    # and both must hold for overall correctness.
    record["target_match_mode"] = target_match_mode
    record["expected_target_count"] = (
        len(expected_object_ids) if require_all_targets else None
    )
    resolved_expected_targets: list[str] = []
    missing_expected_targets: list[str] = []
    if require_all_targets:
        for target_id in sorted(expected_object_ids):
            satisfied = any(
                _status_target_match(resolutions[index], expected_status, {target_id})
                and _canonical_match(resolutions[index], {target_id})
                for index in status_target_satisfying | satisfying
            )
            if satisfied:
                resolved_expected_targets.append(target_id)
            else:
                missing_expected_targets.append(target_id)
    record["resolved_expected_targets"] = list(resolved_expected_targets)
    record["missing_expected_targets"] = list(missing_expected_targets)

    isolation_valid: bool | None = None
    isolation_details: list[str] = []
    isolation_tokens = case.get("isolation_tokens") or {}
    if isolation_tokens:
        isolation_valid = True
        for mention_text, forbidden_tokens in sorted(isolation_tokens.items()):
            for resolution in resolutions:
                if _normalization_key(resolution.mention_text) != _normalization_key(mention_text):
                    continue
                evidence_blob = " ".join(
                    str(item.detail) for item in resolution.evidence
                ).lower()
                leaked = [
                    token
                    for token in forbidden_tokens
                    if token.lower() in evidence_blob
                ]
                if leaked:
                    isolation_valid = False
                    isolation_details.append(
                        f"mention {mention_text!r} evidence leaked tokens {leaked}"
                    )
        if not isolation_details:
            isolation_details.append("no cross-mention token leakage observed")
    record["mention_isolation_valid"] = isolation_valid
    record["isolation_details"] = list(isolation_details)

    targets_ok = (
        (not missing_expected_targets) if require_all_targets else bool(satisfying)
    )
    correct = (
        bool(satisfying)
        and evidence_valid is not False
        and negative_detail is None
        and targets_ok
        and isolation_valid is not False
    )

    allowed_context_object_ids = set(case.get("allowed_context_object_ids") or [])
    classified = _classify_case_decision(
        expected_status=expected_status,
        resolutions=resolutions,
        required_target_ids=set(case["expected_object_ids"]),
        expected_canonical_object_ids=set(case["expected_canonical_object_ids"]),
        allowed_context_object_ids=allowed_context_object_ids,
        require_all_targets=require_all_targets,
        invalid=False,
        isolation_tokens=isolation_tokens,
    )
    decision = classified["decision"]
    record["confident_required_target_ids"] = classified[
        "confident_required_target_ids"
    ]
    record["confident_allowed_context_ids"] = classified[
        "confident_allowed_context_ids"
    ]
    record["confident_unexpected_ids"] = classified["confident_unexpected_ids"]
    record["allowed_context_object_ids"] = sorted(allowed_context_object_ids)
    record["expects_explicit_canonicalization"] = bool(
        case.get("expects_explicit_canonicalization")
    )
    record["explicit_canonicalization_valid"] = None
    if case.get("expects_explicit_canonicalization"):
        # D2-A2R2 repair D: explicit canonicalization requires the resolved
        # canonical target to match AND the evidence to be governed identity
        # (Tier G / accepted alias mechanism), not merely a correct identity.
        canonical_ok = resolution_canonical_target_matches(
            resolutions, set(case["expected_canonical_object_ids"])
        )
        governed = any(
            item.tier == "G" for resolution in resolutions for item in resolution.evidence
        )
        record["explicit_canonicalization_valid"] = bool(canonical_ok and governed)
    # Target-scoped primary-target outcome for positive cases (D2-A2R2
    # repair C/G): coverage and the descriptive summary must follow the
    # required primary target, not any contextual resolution.
    if expected_status == RESOLVED_UNIQUE:
        primary_targets = set(case["expected_object_ids"])
        if any(
            _status_target_match(resolution, expected_status, {target_id})
            and _canonical_match(resolution, {target_id})
            for target_id in sorted(primary_targets)
            for resolution in resolutions
        ):
            record["primary_target_outcome"] = "resolved"
        elif record["has_ambiguous"]:
            record["primary_target_outcome"] = "ambiguous"
        else:
            record["primary_target_outcome"] = "unresolved"
    if decision == "correct_resolve" and evidence_valid is False:
        # A target reached through invalid evidence is not a clean success
        # (D2-A0 contract Section 32/preregistered evidence validity).
        decision = "wrong_resolve"
    correct = decision in {"correct_resolve", "correct_abstain", "correct_ambiguous"}
    record["correct"] = correct
    record["evidence_valid"] = evidence_valid
    record["decision"] = decision
    if not correct and require_all_targets and missing_expected_targets:
        record["failure_detail"] = (
            f"multi-target ALL unsatisfied; missing expected targets: "
            f"{missing_expected_targets}"
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

    if case.get("invalid") is True:
        # D2-A2 §10/A2R1: a case proven objectively invalid is executed
        # read-only for its qualitative receipt, recorded INVALID_CASE with
        # its reason, and excluded from quantitative metrics.  It is never
        # silently replaced.
        record["case_invalid"] = True
        record["correct"] = False
        record["decision"] = "not_applicable"
        record["primary_failure_type"] = CASE_INVALID
        record["failure_detail"] = str(case.get("invalid_reason") or "invalid case")
    return record


# ---------------------------------------------------------------------------
# Metrics and reporting
# ---------------------------------------------------------------------------


def _metric(numerator: int, denominator: int) -> dict[str, int | float]:
    """Every ratio metric carries its numerator/denominator/value explicitly
    (D2-A2R1 repair B); no manually reconstructed denominators."""

    value = numerator / denominator if denominator else 0.0
    return {"numerator": numerator, "denominator": denominator, "value": value}


def _metric(numerator: int, denominator: int) -> dict[str, int | float]:
    """Every ratio metric carries numerator/denominator/value explicitly
    (D2-A2R1 repair B); no manually reconstructed denominators."""

    value = numerator / denominator if denominator else 0.0
    return {"numerator": numerator, "denominator": denominator, "value": value}


def _compute_metrics(
    records: list[dict[str, Any]],
    *,
    not_applicable_categories: list[str] | None = None,
) -> dict[str, Any]:
    """D2-A2R2: target-scoped metrics with num/den/value; case validity,
    natural category applicability, and execution coverage separate; explicit
    canonicalization scoped to cases declaring it."""

    valid = [
        record
        for record in records
        if not record["case_invalid"] and not record["not_applicable"]
    ]
    invalid_records = [record for record in records if record["case_invalid"]]
    decisions = Counter(record["decision"] for record in valid)
    accounting = {bucket: decisions.get(bucket, 0) for bucket in DECISION_BUCKETS}

    positive_cases = [
        record for record in valid if record["expected_status"] == RESOLVED_UNIQUE
    ]
    canonical_expected = [
        record for record in valid if record["expected_canonical_object_ids"]
    ]
    explicit_canonicalization = [
        record for record in valid if record.get("expects_explicit_canonicalization")
    ]
    source_native_null = [
        record
        for record in valid
        if record["expected_canonical_object_ids"] == []
        and record["expected_status"] == RESOLVED_UNIQUE
    ]
    abstain_cases = [
        record for record in valid if record["expected_status"] in ABSTAIN_STATUSES
    ]
    ambiguous_cases = [
        record for record in valid if record["expected_status"] == AMBIGUOUS
    ]
    negative_cases = [
        record for record in valid if record["expected_status"] != RESOLVED_UNIQUE
    ]
    evidence_checked = [
        record
        for record in valid
        if record["expected_resolution_kind"] != "none"
        and record["evidence_valid"] is not None
    ]
    descriptive_cases = [
        record
        for record in valid
        if record["expected_resolution_kind"] == "descriptive_inferential"
    ]

    categories_requiring_accounting = 16
    categories_not_available = len(not_applicable_categories or [])
    categories_natural_applicability = _metric(
        categories_requiring_accounting - categories_not_available,
        categories_requiring_accounting,
    )

    # Target-scoped positive coverage (D2-A2R2 repair C/G): a contextual
    # resolution cannot inflate primary-target coverage.
    positives_covered = sum(
        1
        for record in positive_cases
        if record.get("primary_target_outcome") == "resolved"
    )
    positives_correct = sum(1 for record in positive_cases if record["correct"])

    return {
        "case_counts": {
            "total": len(records),
            "valid": len(valid),
            "invalid": len(invalid_records),
            "invalid_case_ids": sorted(
                record["case_id"] for record in invalid_records
            ),
            "not_applicable": sum(
                1 for record in records if record["not_applicable"]
            ),
            "correct": sum(1 for record in valid if record["correct"]),
        },
        # D2-A2R2 §28: the formal failure taxonomy applies to valid cases
        # only; invalid cases are accounted via case_counts.invalid_case_ids.
        "failure_taxonomy_counts": dict(
            sorted(
                Counter(
                    str(record["primary_failure_type"])
                    for record in valid
                    if record["primary_failure_type"]
                ).items()
            )
        ),
        "decision_accounting": accounting,
        "case_validity": _metric(len(valid), len(records)),
        "category_natural_applicability": {
            **categories_natural_applicability,
            "categories_requiring_accounting": categories_requiring_accounting,
            "not_available_categories": list(not_applicable_categories or []),
            "represented_categories": sorted(
                {str(record["category"]) for record in valid}
            ),
        },
        "execution_coverage": _metric(
            sum(1 for record in records if record["actual"]), len(records)
        ),
        "resolution_accuracy": _metric(
            sum(1 for record in positive_cases if record["correct"]),
            len(positive_cases),
        ),
        "canonical_identity_accuracy": _metric(
            sum(1 for record in canonical_expected if record["correct"]),
            len(canonical_expected),
        ),
        "explicit_canonicalization_accuracy": _metric(
            sum(1 for record in explicit_canonicalization if record["correct"]),
            len(explicit_canonicalization),
        ),
        "source_native_noncanonicalization_accuracy": _metric(
            sum(1 for record in source_native_null if record["correct"]),
            len(source_native_null),
        ),
        "abstention_accuracy": _metric(
            sum(1 for record in abstain_cases if record["correct"]), len(abstain_cases)
        ),
        "ambiguity_accuracy": _metric(
            sum(1 for record in ambiguous_cases if record["correct"]),
            len(ambiguous_cases),
        ),
        "false_positive_resolution_rate": _metric(
            sum(1 for record in negative_cases if record["has_confident_resolve"]),
            len(negative_cases),
        ),
        "evidence_validity": {
            **_metric(
                sum(
                    1
                    for record in evidence_checked
                    if record["evidence_valid"] is True
                ),
                len(evidence_checked),
            ),
            "evidence_checked_cases": len(evidence_checked),
            "evidence_valid_cases": sum(
                1 for record in evidence_checked if record["evidence_valid"] is True
            ),
            "evidence_invalid_cases": sum(
                1 for record in evidence_checked if record["evidence_valid"] is False
            ),
        },
        "positive_resolution_coverage": _metric(
            positives_covered,
            len(positive_cases),
        ),
        "correct_positive_resolution_coverage": _metric(
            positives_correct,
            len(positive_cases),
        ),
        "descriptive_resolution_summary": {
            "descriptive_positive_cases": len(descriptive_cases),
            "descriptive_correctly_resolved": sum(
                1 for record in descriptive_cases if record["correct"]
            ),
            "descriptive_ambiguous": sum(
                1
                for record in descriptive_cases
                if record.get("primary_target_outcome") == "ambiguous"
            ),
            "descriptive_unresolved": sum(
                1
                for record in descriptive_cases
                if record.get("primary_target_outcome") == "unresolved"
            ),
            "descriptive_wrong_confident": sum(
                1 for record in descriptive_cases if record["decision"] == "wrong_resolve"
            ),
        },
        "corrective_handling_correct": sum(
            1
            for record in valid
            if record["expected_resolution_kind"] == "corrective" and record["correct"]
        ),
        "corrective_handling_incorrect": sum(
            1
            for record in valid
            if record["expected_resolution_kind"] == "corrective"
            and not record["correct"]
        ),
    }


def _validate_metric_consistency(
    records: list[dict[str, Any]],
    metrics: dict[str, Any],
) -> list[str]:
    """D2-A2R2 §24: expanded internal consistency assertions."""

    problems: list[str] = []

    def _check(name: str, metric: dict[str, Any]) -> None:
        if metric.get("denominator") and abs(
            metric["numerator"] / metric["denominator"] - metric["value"]
        ) > 1e-9:
            problems.append(f"metric {name}: value != numerator/denominator")
        if metric["numerator"] > metric["denominator"]:
            problems.append(f"metric {name}: numerator > denominator")

    valid = [
        record
        for record in records
        if not record["case_invalid"] and not record["not_applicable"]
    ]
    accounting = metrics.get("decision_accounting", {})
    counted = sum(count for bucket, count in accounting.items())
    if counted != len(valid):
        problems.append("decision_accounting does not sum to valid case count")

    taxonomy = metrics.get("failure_taxonomy_counts", {})
    per_case_failures = Counter(
        str(record["primary_failure_type"])
        for record in valid
        if record["primary_failure_type"]
    )
    if dict(per_case_failures) != taxonomy:
        problems.append("failure_taxonomy_counts do not match valid per-case records")

    for name, metric in metrics.items():
        if isinstance(metric, dict) and "numerator" in metric:
            _check(name, metric)
        elif isinstance(metric, dict):
            for sub_name, sub_metric in metric.items():
                if isinstance(sub_metric, dict) and "numerator" in sub_metric:
                    _check(f"{name}.{sub_name}", sub_metric)

    descriptive = metrics.get("descriptive_resolution_summary", {})
    if descriptive:
        reconciled = (
            descriptive.get("descriptive_correctly_resolved", 0)
            + descriptive.get("descriptive_ambiguous", 0)
            + descriptive.get("descriptive_unresolved", 0)
            + descriptive.get("descriptive_wrong_confident", 0)
        )
        if reconciled != descriptive.get("descriptive_positive_cases"):
            problems.append("descriptive summary does not reconcile")

    return problems


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
    counts = metrics["case_counts"]
    print(
        f"cases: total={counts['total']} valid={counts['valid']} "
        f"correct={counts['correct']} "
        f"not_applicable={counts['not_applicable']} "
        f"invalid={counts['invalid']}"
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
        "canonical_identity_accuracy",
        "explicit_canonicalization_accuracy",
        "source_native_noncanonicalization_accuracy",
        "abstention_accuracy",
        "ambiguity_accuracy",
        "false_positive_resolution_rate",
        "case_validity",
        "category_natural_applicability",
        "execution_coverage",
        "evidence_validity",
    ):
        metric = metrics[name]
        print(f"{name}: {metric['numerator']}/{metric['denominator']} = {metric['value']}")
    coverage = metrics["positive_resolution_coverage"]
    print(
        f"positive_resolution_coverage: {coverage['numerator']}/{coverage['denominator']} "
        f"= {coverage['value']}"
    )
    print(
        f"descriptive summary: {json.dumps(metrics['descriptive_resolution_summary'])}"
    )
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


BEGIN_D2_A2_METRICS = "BEGIN_D2_A2_METRICS"
END_D2_A2_METRICS = "END_D2_A2_METRICS"

# Aggregate keys hoisted from ``metrics`` to the projection top level; they
# stay in the projection exactly once (either hoisted or under ``metrics``).
_PROJECTION_HOISTED_METRIC_KEYS = (
    "case_counts",
    "decision_accounting",
    "failure_taxonomy_counts",
    "descriptive_resolution_summary",
)

# Minimal run-provenance subset kept for provenance validation; receipts,
# state dumps, and per-case diagnostics are deliberately excluded (the
# authoritative results artifact carries all of them).
_PROJECTION_PROVENANCE_KEYS = ("head", "baseline_commit", "timestamp_utc", "case_count")


def build_report_metrics_projection(results: dict[str, Any]) -> dict[str, Any]:
    """Compact, tamper-checkable projection of the D2-A2 results artifact for
    the report's embedded metrics block.

    Contains ONLY aggregate data — no ``per_case_results``, no raw receipts,
    no state dumps, no candidate diagnostics: the hoisted aggregates
    ``case_counts`` / ``decision_accounting`` / ``failure_taxonomy_counts`` /
    ``descriptive_resolution_summary``, the remaining compact ``metrics``
    (num/den/value ratios and small aggregates), a compact per-category
    decision summary, and a tiny ``run_provenance`` subset.  Both
    ``render_metrics_block`` and ``validate_report_metrics`` build on this
    function, so the rendered schema cannot drift from the validated schema.
    """

    metrics = results.get("metrics") or {}
    projection: dict[str, Any] = {
        "case_counts": metrics.get("case_counts"),
        "decision_accounting": metrics.get("decision_accounting"),
        "failure_taxonomy_counts": metrics.get("failure_taxonomy_counts"),
        "metrics": {
            name: value
            for name, value in metrics.items()
            if name not in _PROJECTION_HOISTED_METRIC_KEYS
        },
        "descriptive_resolution_summary": metrics.get(
            "descriptive_resolution_summary"
        ),
    }
    category_summaries = results.get("category_summaries") or {}
    if category_summaries:
        projection["category_summaries"] = {
            category: {
                "cases": summary.get("cases"),
                "correct": summary.get("correct"),
                "decisions": summary.get("decisions"),
            }
            for category, summary in sorted(category_summaries.items())
        }
    provenance = results.get("run_provenance") or {}
    projection["run_provenance"] = {
        key: provenance[key]
        for key in _PROJECTION_PROVENANCE_KEYS
        if key in provenance
    }
    return projection


def render_metrics_block(results: dict[str, Any]) -> str:
    """Render the compact machine-readable metrics block embedded in the
    report (per-case receipts remain only in the results artifact)."""

    projection = build_report_metrics_projection(results)
    lines = [
        BEGIN_D2_A2_METRICS,
        "```json",
        json.dumps(projection, ensure_ascii=False, indent=1, default=str),
        "```",
        END_D2_A2_METRICS,
        "",
    ]
    return "\n".join(lines)


def validate_report_metrics(report_text: str, results: dict[str, Any]) -> list[str]:
    """D2-A2R2 repair E: mechanically compare the report's embedded metrics
    block against the structured results.  The expected block is the compact
    projection built by ``build_report_metrics_projection`` — the same function
    the renderer uses, so the validated schema cannot drift from the rendered
    schema.  Mismatches are reported per key (nested dicts are descended).
    Returns problems ([] = clean)."""

    problems: list[str] = []
    start = report_text.find(BEGIN_D2_A2_METRICS)
    end = report_text.find(END_D2_A2_METRICS)
    if start < 0 or end < 0 or end < start:
        return ["report is missing the BEGIN/END_D2_A2_METRICS block"]
    inner_lines: list[str] = []
    inside = False
    for line in report_text[start:end].splitlines():
        stripped = line.strip()
        if stripped == BEGIN_D2_A2_METRICS:
            inside = True
            continue
        if stripped == END_D2_A2_METRICS:
            break
        if inside and stripped and not stripped.startswith("```"):
            inner_lines.append(line)
    try:
        reported = json.loads("\n".join(inner_lines))
    except json.JSONDecodeError as exc:
        return [f"report metrics block is not valid JSON: {exc}"]
    if not isinstance(reported, dict):
        return ["report metrics block is not a JSON object"]

    def _compare(path: str, expected: Any, observed: Any) -> None:
        if expected == observed:
            return
        if isinstance(expected, dict) and isinstance(observed, dict):
            for key in sorted(set(expected) | set(observed)):
                child = f"{path}.{key}" if path else str(key)
                _compare(child, expected.get(key), observed.get(key))
        else:
            problems.append(f"report {path} mismatch")

    _compare("", build_report_metrics_projection(results), reported)
    return problems


def resolution_canonical_target_matches(
    resolutions: list[Any], expected_canonical_ids: set[str]
) -> bool:
    """True when some resolution's canonical target matches the expected
    canonical identity (used by explicit-canonicalization cases)."""

    return any(
        resolution.canonical_object_id in expected_canonical_ids
        for resolution in resolutions
    )


def run(
    project_root: Path,
    cases_path: Path,
    results_path: Path,
    receipt_baseline_path: Path | None = None,
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
    not_applicable_categories = [
        str(item.get("category"))
        for item in not_applicable_records
        if isinstance(item, dict) and item.get("category")
    ]
    metrics = _compute_metrics(
        records, not_applicable_categories=not_applicable_categories
    )
    consistency_problems = _validate_metric_consistency(records, metrics)
    if consistency_problems:
        raise RuntimeError(
            "metric consistency assertions failed: "
            + "; ".join(consistency_problems)
        )
    categories = _category_summaries(records)
    receipt_consistency = None
    if receipt_baseline_path is not None and receipt_baseline_path.exists():
        baseline = json.loads(receipt_baseline_path.read_text(encoding="utf-8"))
        baseline_by_id = {
            item["case_id"]: item for item in baseline.get("per_case_results", [])
        }
        comparisons = []
        skipped_invalid: list[str] = []
        for record in records:
            baseline_record = baseline_by_id.get(str(record["case_id"]))
            if baseline_record is None:
                continue
            if record.get("case_invalid") or baseline_record.get("case_invalid"):
                # Invalid cases are excluded from the resolver-behavior
                # comparison: C14's difference is the documented D2-A2R1 §41
                # evaluation-state correction (the declared function row made
                # the previously unmatchable symbol resolvable).
                skipped_invalid.append(str(record["case_id"]))
                continue
            current_receipt = (record.get("actual") or {}).get("receipt") or {}
            baseline_receipt = (baseline_record.get("actual") or {}).get("receipt") or {}

            def _signature(receipt: dict[str, Any]) -> list[Any]:
                signature = []
                for resolution in receipt.get("resolutions", []):
                    signature.append(
                        {
                            "mention_text": resolution.get("mention_text"),
                            "mention_kind": resolution.get("mention_kind"),
                            "status": resolution.get("status"),
                            "matched_object_id": resolution.get("matched_object_id"),
                            "canonical_object_id": resolution.get(
                                "canonical_object_id"
                            ),
                            "evidence": [
                                {"tier": item.get("tier"), "kind": item.get("kind")}
                                for item in resolution.get("evidence", [])
                            ],
                            "candidate_ids": sorted(
                                item.get("object_id", "")
                                for item in resolution.get("candidates", [])
                            ),
                        }
                    )
                return signature

            same = _signature(current_receipt) == _signature(baseline_receipt)
            comparisons.append(
                {
                    "case_id": str(record["case_id"]),
                    "receipts_identical": same,
                }
            )
        mismatches = [
            item["case_id"] for item in comparisons if not item["receipts_identical"]
        ]
        receipt_consistency = {
            "baseline_commit": "ae7b281",
            "baseline_artifact": str(receipt_baseline_path),
            "compared_cases": len(comparisons),
            "identical_receipts": sum(
                1 for item in comparisons if item["receipts_identical"]
            ),
            "mismatched_case_ids": mismatches,
            "skipped_invalid_cases": skipped_invalid,
            "resolver_behavior_unchanged": not mismatches,
        }

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
        "failure_taxonomy_counts": metrics["failure_taxonomy_counts"],
        "category_summaries": categories,
        "per_case_results": records,
        "not_applicable_records": not_applicable_records,
        "metric_consistency_problems": consistency_problems,
        "receipt_consistency_vs_ae7b281": receipt_consistency,
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
    parser.add_argument("--receipt-baseline", default=None)
    args = parser.parse_args(argv)
    run(
        Path(args.project_root),
        Path(args.cases),
        Path(args.results),
        receipt_baseline_path=(
            Path(args.receipt_baseline) if args.receipt_baseline else None
        ),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
