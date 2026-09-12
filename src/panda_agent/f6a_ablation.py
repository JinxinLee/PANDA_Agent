"""F6-A evaluation-only benchmark-dependency ablation overlay.

The preregistered F6-A ablation removes the reviewed query-expansion injection
(the D4-owned YAML trigger rule layer: matched symbols/concepts/repositories/
page hints) from the retrieval analyzer while leaving every other behavior of
the frozen candidate untouched. It is a runtime overlay for the isolated
ablation process only: no file, config, or product code changes.
"""

from __future__ import annotations

import contextlib
from typing import Any, Iterator

from panda_agent.config import QueryExpansions


_ABLATION_SCHEMA_VERSION = "f6a-ablation-disabled-query-expansions"
_DESCRIPTION = (
    "Disable the reviewed query-expansion injection layer (D4-owned YAML "
    "trigger rules contributing symbols/concepts/repositories/page hints); "
    "all other candidate behavior is identical to the primary candidate."
)


@contextlib.contextmanager
def install() -> Iterator[dict[str, Any]]:
    """Disable reviewed query-expansion injection for the caller's process.

    Yields the ablation manifest entry describing the single enforced
    difference from the primary candidate.
    """
    import panda_agent.retrieval as retrieval

    disabled = QueryExpansions(schema_version=_ABLATION_SCHEMA_VERSION, rules=[])
    original = retrieval.load_query_expansions

    def _ablated_load(path: Any) -> QueryExpansions:
        return disabled

    retrieval.load_query_expansions = _ablated_load
    try:
        yield {
            "ablation_id": "disable_query_expansion_injection",
            "description": _DESCRIPTION,
            "changed_surfaces": ["retrieval.query_expansions"],
            "unchanged_surfaces": [
                "qa",
                "prompts",
                "models",
                "retrieval_policies",
                "index",
                "runtime_mode",
            ],
        }
    finally:
        retrieval.load_query_expansions = original
