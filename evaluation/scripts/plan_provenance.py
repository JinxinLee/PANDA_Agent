"""Evaluation-only fail-fast plan provenance guard.

Prevents C4-style minimal plan records from silently becoming executable
RetrievalPlans through pydantic defaults.  Every candidate-generating field
consumed by the current retrieval stack must be an explicitly recorded key;
a faithfully recorded empty value (e.g. ``[]``) is valid, a missing key that
would default to empty is not.  Production retrieval does not import this.
"""

from __future__ import annotations

REQUIRED_EXECUTABLE_PLAN_FIELDS = (
    "intent",
    "target_repositories",
    "resolved_versions",
    "symbols",
    "concepts",
    "resolved_aliases",
    "required_source_types",
    "paper_page_hints",
    "analysis_diagnostics",
    "source_budgets",
)


def validate_executable_plan_payload(payload: dict) -> None:
    """Assert every candidate-generating field is explicitly present."""

    if not isinstance(payload, dict):
        raise TypeError("executable plan payload must be a mapping")
    missing = [
        field for field in REQUIRED_EXECUTABLE_PLAN_FIELDS if field not in payload
    ]
    if missing:
        raise ValueError(
            "plan payload is not a complete executable RetrievalPlan; missing "
            f"explicit fields {missing} (model defaults may not create "
            "executable-plan semantics)"
        )
