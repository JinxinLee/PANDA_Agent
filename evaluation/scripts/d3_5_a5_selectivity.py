"""D3.5-A5 — deterministic bridge-selectivity prototype (evaluation-only).

Implements exactly one preregistered generic deterministic selectivity policy
for governed provenance-backed bridge candidates, per the frozen D3.5-A4
design (SELECTIVITY_CAP = 8, PER_ORIGIN_CAP = 4, zero model calls, zero extra
embeddings).  It reads only the frozen replay fixture; it never touches the
runtime retriever, D1, D2, query expansions, or any model surface.

Governance eligibility is a hard prerequisite: the input universe is the
fixture's eligible governed bridge candidates; selectivity only orders,
filters, and caps among them and never introduces a candidate.

Modes:
  --run-synthetic-tests   run the preregistered synthetic unit checks
                          (Phase-2 freeze gate; no real A2 cases used)
  --run-replay            Phase-3 deterministic replay of the six frozen A2
                          development cases through the frozen policy

CLI:
    PYTHONPATH=src python evaluation/scripts/d3_5_a5_selectivity.py \
        --project-root . --run-synthetic-tests
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

SELECTIVITY_POLICY_VERSION = "d3_5_a5_selectivity_v1"
SELECTIVITY_CAP = 8
PER_ORIGIN_CAP = 4
MIN_PRIMARY_SCORE = 1
NON_GRAPH_CHANNELS = ("exact", "dense", "sparse", "paper", "workflow")
GRAPH_CHANNEL_LIMIT = 20

# ---------------------------------------------------------------------------
# Frozen tokenizer contract (preregistered; identical rule for every query and
# candidate string; no filename-specific handling).
# ---------------------------------------------------------------------------


def tokenize(text: str) -> set[str]:
    """Frozen deterministic tokenizer.

    1. Unicode NFKD normalization (case preserved).
    2. Insert a boundary between a lower/digit character and an uppercase
       character (camelCase splitting) — must run before casefolding.
    3. Casefold.
    4. Replace every run of characters outside [a-z0-9] with one space
       (underscores, dots, slashes, hyphens, punctuation are separators).
    5. Split on whitespace; drop empty tokens.
    6. Deduplicate (set semantics); no stopwords; no stemming.
    """
    normalized = unicodedata.normalize("NFKD", text or "")
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", normalized)
    cleaned = re.sub(r"[^a-z0-9]+", " ", camel_split.casefold())
    return {token for token in cleaned.split() if token}


def query_token_set(question: str, plan: dict[str, Any]) -> set[str]:
    tokens: set[str] = set(tokenize(question))
    for concept in plan.get("concepts") or []:
        tokens |= tokenize(str(concept))
    for symbol in plan.get("symbols") or []:
        tokens |= tokenize(str(symbol))
    return tokens


def candidate_tokens(locator_path: str | None, title: str | None) -> tuple[set[str], set[str]]:
    return tokenize(locator_path or ""), tokenize(title or "")


# ---------------------------------------------------------------------------
# Preregistered scoring contract
# ---------------------------------------------------------------------------


def plan_scope_set(plan: dict[str, Any]) -> set[str]:
    scope: set[str] = set()
    scope |= {str(item) for item in plan.get("target_repositories") or []}
    scope |= {str(item) for item in plan.get("version_repositories") or []}
    scope |= {str(key) for key in (plan.get("resolved_versions") or {})}
    return scope


def support_rank(candidate_id: str, channels: dict[str, list[str]]) -> int | None:
    ranks = []
    for channel in NON_GRAPH_CHANNELS:
        ordering = channels.get(channel) or []
        if candidate_id in ordering:
            ranks.append(ordering.index(candidate_id) + 1)
    return min(ranks) if ranks else None


def select_bridge_candidates(
    case: dict[str, Any],
    payload_registry: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Run the frozen selectivity policy for one case.  Pure function."""
    plan = case.get("frozen_plan_fields") or {}
    question = ((case.get("question") or {}).get("query")) or ""
    query_tokens = query_token_set(question, plan)
    scope = plan_scope_set(plan)
    channels = ((case.get("arms") or {}).get("STRUCTURED_BRIDGED") or {}).get(
        "channel_rankings"
    ) or {}
    unbridged_graph = case.get("unbridged_graph_ordering") or []
    unbridged_set = set(unbridged_graph)

    receipts: list[dict[str, Any]] = []
    for candidate in case.get("eligible_governed_bridge_candidates") or []:
        object_id = candidate["candidate_object_id"]
        payload = payload_registry.get(object_id) or {}
        path_tokens, title_tokens = candidate_tokens(
            candidate.get("locator_path"), payload.get("title")
        )
        path_overlap = len(query_tokens & path_tokens)
        title_overlap = len(query_tokens & title_tokens)
        primary_score = path_overlap + title_overlap
        sources = {candidate.get("source_id")}
        scope_rejected = bool(scope) and sources.isdisjoint(scope)
        support = support_rank(object_id, channels)
        distance = candidate.get("min_structural_distance_transitions")
        if distance is None:
            distance = 1_000_000  # missing distance sorts last, deterministically
        if scope_rejected:
            disposition = "scope_rejected"
        elif primary_score < MIN_PRIMARY_SCORE:
            disposition = "zero_score_rejected"
        else:
            disposition = "candidate"
        receipts.append(
            {
                "candidate_object_id": object_id,
                "locator_path": candidate.get("locator_path"),
                "source_id": candidate.get("source_id"),
                "source_version_id": candidate.get("source_version_id"),
                "provenance_origin_ids": sorted(
                    candidate.get("provenance_origin_ids") or []
                ),
                "a2_disposition": candidate.get("a2_disposition"),
                "path_overlap": path_overlap,
                "title_overlap": title_overlap,
                "primary_score": primary_score,
                "support_rank": support,
                "structural_distance": distance,
                "in_unbridged_graph": object_id in unbridged_set,
                "disposition": disposition,
            }
        )

    candidates = [item for item in receipts if item["disposition"] == "candidate"]
    candidates.sort(
        key=lambda item: (
            -item["primary_score"],
            item["support_rank"] if item["support_rank"] is not None else 1_000_000,
            item["structural_distance"],
            item["candidate_object_id"],
        )
    )

    origin_used: dict[str, int] = {}
    selected: list[dict[str, Any]] = []
    origin_capped_out = 0
    beyond_selectivity_cap = 0
    for item in candidates:
        if len(selected) >= SELECTIVITY_CAP:
            item["disposition"] = "beyond_selectivity_cap"
            beyond_selectivity_cap += 1
            continue
        origins = sorted(item["provenance_origin_ids"])
        chosen = min(origins, key=lambda origin: (origin_used.get(origin, 0), origin))
        if origin_used.get(chosen, 0) >= PER_ORIGIN_CAP:
            item["disposition"] = "origin_capped_out"
            origin_capped_out += 1
            continue
        origin_used[chosen] = origin_used.get(chosen, 0) + 1
        item["attributed_origin_id"] = chosen
        item["disposition"] = "selected"
        selected.append(item)

    # --- deterministic selectivity-only graph reconstruction ------------------
    def merge_ids(prefix: list[str], rows: list[str], limit: int) -> list[str]:
        merged, seen = [], set()
        for oid in [*prefix, *rows]:
            if oid in seen:
                continue
            seen.add(oid)
            merged.append(oid)
            if len(merged) >= limit:
                break
        return merged

    selected_ids_in_order = [item["candidate_object_id"] for item in selected]
    a5_graph = merge_ids(selected_ids_in_order, unbridged_graph, GRAPH_CHANNEL_LIMIT)
    displaced_after = [oid for oid in unbridged_graph if oid not in a5_graph]
    baseline_admitted = case.get("baseline_old_cap_admitted_ids_injection_order") or []
    baseline_graph = case.get("baseline_bridged_graph_ordering_recomputed") or []
    displaced_before = case.get("baseline_ordinary_graph_displaced_ids_before") or []

    origins_before = {
        origin
        for item in case.get("eligible_governed_bridge_candidates") or []
        for origin in (item.get("provenance_origin_ids") or [])
    }
    origins_baseline_admitted = {
        origin
        for item in case.get("eligible_governed_bridge_candidates") or []
        if item.get("a2_disposition") == "A2_ADMITTED"
        for origin in (item.get("provenance_origin_ids") or [])
    }
    origins_after = {origin for item in selected for origin in item["provenance_origin_ids"]}
    # Cap-consistent accounting: counts follow the attributed origin (the same
    # semantics the PER_ORIGIN_CAP is enforced with), so attributed counts are
    # always <= PER_ORIGIN_CAP.  Membership counts (a selected candidate may
    # belong to several origins) are reported separately as informational.
    per_origin_retained = {
        origin: sum(1 for item in selected if item.get("attributed_origin_id") == origin)
        for origin in sorted(origins_after)
    }
    per_origin_membership = {
        origin: sum(1 for item in selected if origin in item["provenance_origin_ids"])
        for origin in sorted(origins_after)
    }
    graph_admitted_bridge = [oid for oid in selected_ids_in_order if oid in a5_graph]
    overlap_non_graph = [
        item["candidate_object_id"]
        for item in selected
        if item["support_rank"] is not None
    ]

    return {
        "case_id": case.get("case_id"),
        "query_token_count": len(query_tokens),
        "plan_scope": sorted(scope),
        "eligible_governed_bridge_candidate_count": case.get(
            "eligible_governed_bridge_candidate_count"
        ),
        "baseline_old_cap_admitted_count": len(baseline_admitted),
        "selected_bridge_candidate_count": len(selected),
        "selection_reduction_count": (case.get("eligible_governed_bridge_candidate_count") or 0)
        - len(selected),
        "selection_reduction_ratio": round(
            1
            - (len(selected) / (case.get("eligible_governed_bridge_candidate_count") or 1)),
            6,
        ),
        "number_of_provenance_origins_before": len(origins_before),
        "number_of_provenance_origins_baseline_admitted": len(origins_baseline_admitted),
        "number_of_provenance_origins_after": len(origins_after),
        "per_origin_retained_counts": per_origin_retained,
        "per_origin_membership_counts": per_origin_membership,
        "selected_candidates": [
            {
                "candidate_object_id": item["candidate_object_id"],
                "locator_path": item["locator_path"],
                "source_id": item["source_id"],
                "source_version_id": item["source_version_id"],
                "path_overlap": item["path_overlap"],
                "title_overlap": item["title_overlap"],
                "primary_score": item["primary_score"],
                "support_rank": item["support_rank"],
                "structural_distance": item["structural_distance"],
                "provenance_origin_ids": item["provenance_origin_ids"],
                "attributed_origin_id": item.get("attributed_origin_id"),
                "a2_disposition": item["a2_disposition"],
            }
            for item in selected
        ],
        "candidate_receipts": receipts,
        "zero_score_candidates_rejected": sum(
            1 for item in receipts if item["disposition"] == "zero_score_rejected"
        ),
        "scope_rejected_count": sum(
            1 for item in receipts if item["disposition"] == "scope_rejected"
        ),
        "origin_capped_out_count": origin_capped_out,
        "beyond_selectivity_cap_count": beyond_selectivity_cap,
        "graph_admitted_bridge_candidates": graph_admitted_bridge,
        "graph_admitted_bridge_candidate_count": len(graph_admitted_bridge),
        "ordinary_graph_candidates_displaced_before_count": len(displaced_before),
        "ordinary_graph_candidates_displaced_after_count": len(displaced_after),
        "ordinary_graph_candidates_displaced_after_ids": displaced_after,
        "overlap_with_non_graph_channels_count": len(overlap_non_graph),
        "overlap_with_non_graph_channels_ids": overlap_non_graph,
        "selectivity_only_graph_ordering": a5_graph,
        "baseline_ordinary_graph_displaced_ids_before": displaced_before,
        "baseline_graph_admitted_bridge_candidates": [
            oid
            for oid in baseline_admitted
            if oid in set(baseline_graph)
        ],
    }


# ---------------------------------------------------------------------------
# Synthetic unit checks (Phase-2 freeze gate; no real A2 cases)
# ---------------------------------------------------------------------------


def _synthetic_case(
    eligible: list[dict[str, Any]],
    question: str,
    plan: dict[str, Any] | None = None,
    channels: dict[str, list[str]] | None = None,
    unbridged_graph: list[str] | None = None,
    admitted: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": "SYNTHETIC",
        "question": {"query": question, "query_sha256": "0" * 64},
        "frozen_plan_fields": plan or {},
        "eligible_governed_bridge_candidates": eligible,
        "eligible_governed_bridge_candidate_count": len(eligible),
        "baseline_old_cap_admitted_ids_injection_order": admitted or [],
        "unbridged_graph_ordering": unbridged_graph or [],
        "baseline_bridged_graph_ordering_recomputed": [],
        "baseline_ordinary_graph_displaced_ids_before": [],
        "arms": {
            "STRUCTURED_BRIDGED": {"channel_rankings": channels or {}},
        },
    }


def _synthetic_candidate(
    object_id: str,
    locator_path: str,
    origins: list[str],
    source_id: str = "synthetic_repo",
    title: str = "synthetic title",
    distance: int = 1,
    a2_disposition: str = "A2_CAPPED_OUT",
) -> dict[str, Any]:
    return {
        "candidate_object_id": object_id,
        "provenance_origin_ids": origins,
        "source_id": source_id,
        "source_version_id": f"{source_id}@synthetic",
        "locator_path": locator_path,
        "min_structural_distance_transitions": distance,
        "a2_disposition": a2_disposition,
    }


def run_synthetic_tests() -> list[str]:
    failures: list[str] = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            failures.append(name)

    registry = {
        f"object.{i:024d}": {
            "object_id": f"object.{i:024d}",
            "title": "synthetic title",
            "source_id": "synthetic_repo",
            "text_payload_2000": "x" * 10,
        }
        for i in range(40)
    }

    def oid(i: int) -> str:
        return f"object.{i:024d}"

    question = "restgas profile reconstruction workflow"
    base_plan = {
        "concepts": ["restgas profile"],
        "symbols": [],
        "target_repositories": [],
        "version_repositories": [],
        "resolved_versions": {},
    }

    # 1. score ordering: stronger lexical overlap ranks first (both relevant)
    case = _synthetic_case(
        [
            _synthetic_candidate(oid(1), "reconstruction/workflow/other.c", ["originA"]),
            _synthetic_candidate(oid(2), "restgas/profile/reconstruction.c", ["originA"]),
        ],
        question,
        base_plan,
    )
    result = select_bridge_candidates(case, registry)
    check(
        "score-ordering",
        len(result["selected_candidates"]) == 2
        and result["selected_candidates"][0]["candidate_object_id"] == oid(2)
        and result["selected_candidates"][0]["primary_score"]
        > result["selected_candidates"][1]["primary_score"],
    )

    # 2. zero-score fail-closed: no overlap -> nothing selected despite slots
    case = _synthetic_case(
        [_synthetic_candidate(oid(3), "totally/different/file.cxx", ["originB"])],
        question,
        base_plan,
    )
    result = select_bridge_candidates(case, registry)
    check(
        "zero-score-fail-closed",
        result["selected_bridge_candidate_count"] == 0
        and result["zero_score_candidates_rejected"] == 1,
    )

    # 3. scope rejection: plan scope excludes the candidate's source
    case = _synthetic_case(
        [_synthetic_candidate(oid(4), "macro/target/restgas_profile.c", ["originA"], source_id="other_repo")],
        question,
        {**base_plan, "target_repositories": ["synthetic_repo"]},
    )
    result = select_bridge_candidates(case, registry)
    check(
        "scope-rejection",
        result["selected_bridge_candidate_count"] == 0
        and result["scope_rejected_count"] == 1,
    )

    # 4. scope filter is not a bonus: in-scope and scope-compatible equal scores
    case = _synthetic_case(
        [
            _synthetic_candidate(oid(5), "macro/target/restgas_a.c", ["originA"], source_id="synthetic_repo"),
            _synthetic_candidate(oid(6), "macro/target/restgas_b.c", ["originB"], source_id="synthetic_repo"),
        ],
        "restgas",
        {**base_plan, "target_repositories": ["synthetic_repo"]},
    )
    result = select_bridge_candidates(case, registry)
    scores = [item["primary_score"] for item in result["selected_candidates"]]
    check("scope-no-bonus", len(result["selected_candidates"]) == 2 and scores == [1, 1])

    # 5. PER_ORIGIN_CAP = 4 with a single origin (single-origin behavior)
    case = _synthetic_case(
        [
            _synthetic_candidate(oid(10 + i), f"restgas/file_{i}.c", ["originA"])
            for i in range(6)
        ],
        "restgas",
        base_plan,
    )
    result = select_bridge_candidates(case, registry)
    check(
        "per-origin-cap",
        result["selected_bridge_candidate_count"] == 4
        and result["origin_capped_out_count"] == 2,
    )

    # 6. SELECTIVITY_CAP = 8 ceiling across many origins
    case = _synthetic_case(
        [
            _synthetic_candidate(oid(20 + i), f"restgas/file_{i}.c", [f"origin{i}"])
            for i in range(12)
        ],
        "restgas",
        base_plan,
    )
    result = select_bridge_candidates(case, registry)
    check(
        "selectivity-cap",
        result["selected_bridge_candidate_count"] == 8
        and result["beyond_selectivity_cap_count"] == 4,
    )

    # 7. multi-origin: candidate in a capped origin survives via its second origin
    case = _synthetic_case(
        [
            _synthetic_candidate(oid(30), "restgas/a.c", ["originA", "originB"]),
            *[
                _synthetic_candidate(oid(31 + i), f"restgas/filler_{i}.c", ["originA"])
                for i in range(3)
            ],
        ],
        "restgas",
        base_plan,
    )
    result = select_bridge_candidates(case, registry)
    selected_ids = {item["candidate_object_id"] for item in result["selected_candidates"]}
    check("multi-origin-survival", oid(30) in selected_ids)

    # 8. supporting channel signal breaks ties before structural distance
    case = _synthetic_case(
        [
            _synthetic_candidate(oid(40), "restgas/slow_path/alpha.c", ["originA"], distance=1),
            _synthetic_candidate(oid(41), "restgas/short/beta.c", ["originB"], distance=2),
        ],
        "restgas alpha beta",
        base_plan,
        channels={"sparse": [oid(41)]},
    )
    result = select_bridge_candidates(case, registry)
    check(
        "support-tiebreak-before-distance",
        result["selected_candidates"][0]["candidate_object_id"] == oid(41),
    )

    # 9. structural distance breaks ties after primary score (no support)
    case = _synthetic_case(
        [
            _synthetic_candidate(oid(42), "restgas/deep/alpha.c", ["originA"], distance=2),
            _synthetic_candidate(oid(43), "restgas/short/beta.c", ["originB"], distance=1),
        ],
        "restgas alpha beta",
        base_plan,
    )
    result = select_bridge_candidates(case, registry)
    check(
        "structural-tiebreak",
        result["selected_candidates"][0]["candidate_object_id"] == oid(43),
    )

    # 10. stable object_id final tie-break (equal everything)
    case = _synthetic_case(
        [
            _synthetic_candidate(oid(45), "restgas/zzz.c", ["originA"], distance=1),
            _synthetic_candidate(oid(44), "restgas/aaa.c", ["originB"], distance=1),
        ],
        "restgas",
        base_plan,
    )
    result = select_bridge_candidates(case, registry)
    check(
        "object-id-tiebreak",
        result["selected_candidates"][0]["candidate_object_id"] == oid(44),
    )

    # 11. determinism: identical inputs -> identical outputs (two runs + hash)
    eligible = [
        _synthetic_candidate(oid(50 + i), f"restgas/path_{i}.c", [f"origin{i % 3}"])
        for i in range(20)
    ]
    case = _synthetic_case(eligible, question, base_plan)
    first = json.dumps(select_bridge_candidates(case, registry), sort_keys=True)
    second = json.dumps(select_bridge_candidates(case, registry), sort_keys=True)
    check("determinism", first == second)

    # 12. subset invariant: selected ⊆ eligible
    result = select_bridge_candidates(case, registry)
    universe = {item["candidate_object_id"] for item in case["eligible_governed_bridge_candidates"]}
    selected_ids = {item["candidate_object_id"] for item in result["selected_candidates"]}
    check("selected-subset-eligible", selected_ids <= universe)

    # 13. tokenizer contract: camelCase + separators normalize identically
    check(
        "tokenizer-contract",
        tokenize("PndTargetGenerator.cxx") == {"pnd", "target", "generator", "cxx"}
        and tokenize("restgas_profile") == {"restgas", "profile"}
        and tokenize("Macro Target restgas") == {"macro", "target", "restgas"},
    )

    return failures


# ---------------------------------------------------------------------------
# Phase-3 replay driver
# ---------------------------------------------------------------------------


def run_replay(project_root: Path) -> dict[str, Any]:
    fixture_path = project_root / "evaluation" / "d3_5_downstream_replay_fixture.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    results = {}
    for case_id in fixture["identity"]["case_ids"]:
        case = fixture["cases"][case_id]
        first = select_bridge_candidates(case, fixture["reranker_payload_registry"])
        second = select_bridge_candidates(case, fixture["reranker_payload_registry"])
        if json.dumps(first, sort_keys=True) != json.dumps(second, sort_keys=True):
            raise RuntimeError(f"non-deterministic selectivity output for {case_id}")
        results[case_id] = first
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run-synthetic-tests", action="store_true")
    parser.add_argument("--run-replay", action="store_true")
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    if args.run_synthetic_tests:
        failures = run_synthetic_tests()
        print(f"synthetic tests: {13 - len(failures)}/13 passed")
        for failure in failures:
            print("FAILED:", failure)
        return 1 if failures else 0
    if args.run_replay:
        results = run_replay(project_root)
        print(
            json.dumps(
                {
                    case: {
                        "eligible": result["eligible_governed_bridge_candidate_count"],
                        "baseline_admitted": result["baseline_old_cap_admitted_count"],
                        "selected": result["selected_bridge_candidate_count"],
                        "displaced_before": result[
                            "ordinary_graph_candidates_displaced_before_count"
                        ],
                        "displaced_after": result[
                            "ordinary_graph_candidates_displaced_after_count"
                        ],
                    }
                    for case, result in results.items()
                },
                indent=1,
            )
        )
        out = project_root / "data" / "tmp" / "d3_5_a5_replay_results.json"
        out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("results written to", out)
        return 0
    parser.error("choose --run-synthetic-tests or --run-replay")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
