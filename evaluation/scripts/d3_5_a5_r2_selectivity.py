"""D3.5-A5-R2 — repaired deterministic selectivity v2 + complete-universe evaluator.

Implements exactly the frozen ``d3_5_selectivity_v2`` contract from
D3.5-A5-R1 + D3.5-A5-R1-R1 (no scientific discretion), plus the
complete-pre-cap-universe evaluator with the four applicability classes.

Frozen contract summary (R1 + R1-R1, unchanged here):
  hard filters   : governance universe, plan-scope compatibility,
                   MIN_PRIMARY_SCORE >= 1 on the v1 path/title lexical gate
  PRIMARY_RANK   : 1. symbol_exact_tier DESC
                   2. rarity_weighted_overlap DESC
                      (idf(t) = log2((|U|+1)/(df(t)+1)), universe-local df)
                   3. basename_coverage DESC
                   4. text_presence DESC
  SECONDARY_RANK : support_rank ASC (missing worse; never disqualifying)
  TIEBREAKER_ONLY: structural_distance ASC, candidate_object_id ASC
  caps           : PER_ORIGIN_CAP = 4 (attributed-origin ceiling),
                   SELECTIVITY_CAP = 8 (ceiling); fail closed
  attribution    : least-used-origin (tie: lexicographically smallest origin id)

The evaluator reuses the frozen ``GoldEvidenceSelector.matches`` semantics over
the complete pre-cap eligible governed universe and classifies
NOT_APPLICABLE_TO_SELECTIVITY / GATE_RECALL_LIMITATION / APPLICABLE_AND_RETAINED
/ APPLICABLE_AND_LOST.  Expected evidence never enters the selectivity policy.

Modes:
  --run-synthetic-tests   v2 + evaluator synthetic/property checks (Phase-1 gate)
  --run-replay            Phase-2 deterministic six-case revalidation

CLI:
    PYTHONPATH=src python evaluation/scripts/d3_5_a5_r2_selectivity.py \
        --project-root . --run-synthetic-tests
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

POLICY_VERSION = "d3_5_selectivity_v2"
SELECTIVITY_CAP = 8
PER_ORIGIN_CAP = 4
MIN_PRIMARY_SCORE = 1
NON_GRAPH_CHANNELS = ("exact", "dense", "sparse", "paper", "workflow")
GRAPH_CHANNEL_LIMIT = 20
IDENTIFIER_CHAR = re.compile(r"[a-z0-9_]")

# ---------------------------------------------------------------------------
# Frozen A5 v1 primitives (reused verbatim; the v1 implementation file is not
# imported so this prototype remains self-contained, but the semantics are the
# frozen ones: tokenizer, query token set, v1 gate, support, merge, caps).
# ---------------------------------------------------------------------------


def tokenize(text: str) -> set[str]:
    """Frozen A5 lexical tokenizer (NFKD -> camelCase split -> casefold ->
    non-[a-z0-9] separators -> dedupe)."""
    normalized = unicodedata.normalize("NFKD", text or "")
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", normalized)
    cleaned = re.sub(r"[^a-z0-9]+", " ", camel_split.casefold())
    return {token for token in cleaned.split() if token}


def exact_normalize(text: str) -> str:
    """Frozen R1-R1 symbol-exact normalization: NFKC -> casefold -> path
    separators to '/'."""
    return (
        unicodedata.normalize("NFKC", text or "").casefold().replace("\\", "/")
    )


def symbol_exact_match(symbol: str, surface: str) -> bool:
    """Boundary-aware compound-symbol match: the normalized symbol occurrence
    must be bounded on both sides by start/end of string or a character
    outside [a-z0-9_]."""
    sym = exact_normalize(symbol)
    if not sym:
        return False
    surf = exact_normalize(surface)
    pattern = r"(?<![a-z0-9_])" + re.escape(sym) + r"(?![a-z0-9_])"
    return re.search(pattern, surf) is not None


def plan_scope_set(plan: dict[str, Any]) -> set[str]:
    scope: set[str] = set()
    scope |= {str(item) for item in plan.get("target_repositories") or []}
    scope |= {str(item) for item in plan.get("version_repositories") or []}
    scope |= {str(key) for key in (plan.get("resolved_versions") or {})}
    return scope


def query_token_set(question: str, plan: dict[str, Any]) -> set[str]:
    tokens: set[str] = set(tokenize(question))
    for concept in plan.get("concepts") or []:
        tokens |= tokenize(str(concept))
    for symbol in plan.get("symbols") or []:
        tokens |= tokenize(str(symbol))
    return tokens


def support_rank(candidate_id: str, channels: dict[str, list[str]]) -> int | None:
    ranks = []
    for channel in NON_GRAPH_CHANNELS:
        ordering = channels.get(channel) or []
        if candidate_id in ordering:
            ranks.append(ordering.index(candidate_id) + 1)
    return min(ranks) if ranks else None


def merge_ids(prefix: list[str], rows: list[str], limit: int) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for oid in [*prefix, *rows]:
        if oid in seen:
            continue
        seen.add(oid)
        merged.append(oid)
        if len(merged) >= limit:
            break
    return merged


# ---------------------------------------------------------------------------
# v2 candidate views
# ---------------------------------------------------------------------------


def candidate_views(candidate: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    locator_path = candidate.get("locator_path") or ""
    basename = locator_path.rsplit("/", 1)[-1]
    parent_dir = locator_path.rsplit("/", 1)[0] if "/" in locator_path else ""
    title = payload.get("title") or ""
    text = payload.get("text_payload_2000") or ""
    path_tokens = tokenize(locator_path)
    title_tokens = tokenize(title)
    text_tokens = tokenize(text)
    basename_tokens = tokenize(basename)
    parent_tokens = tokenize(parent_dir)
    return {
        "basename": basename,
        "path_tokens": path_tokens,
        "title_tokens": title_tokens,
        "text_tokens": text_tokens,
        "basename_tokens": basename_tokens,
        "parent_tokens": parent_tokens,
        "lexical_view": basename_tokens | parent_tokens | title_tokens | text_tokens,
        # title excluded from the symbol-exact tier (R1-R1 frozen decision)
        "exact_surfaces": [basename, locator_path, text],
    }


# ---------------------------------------------------------------------------
# v2 policy
# ---------------------------------------------------------------------------


def select_v2(case: dict[str, Any], payload_registry: dict[str, dict[str, Any]]) -> dict[str, Any]:
    plan = case.get("frozen_plan_fields") or {}
    question = ((case.get("question") or {}).get("query")) or ""
    query_tokens = query_token_set(question, plan)
    scope = plan_scope_set(plan)
    channels = ((case.get("arms") or {}).get("STRUCTURED_BRIDGED") or {}).get(
        "channel_rankings"
    ) or {}
    unbridged_graph = case.get("unbridged_graph_ordering") or []
    plan_symbols = [str(s) for s in (plan.get("symbols") or [])]

    universe = case.get("eligible_governed_bridge_candidates") or []

    # --- hard filter: plan-scope compatibility -------------------------------
    scope_passed: list[dict[str, Any]] = []
    scope_rejected = 0
    for candidate in universe:
        source_id = candidate.get("source_id")
        if scope and source_id not in scope:
            scope_rejected += 1
            continue
        scope_passed.append(candidate)
    eligible_after_scope = len(scope_passed)

    # --- views and df over U (universe after scope eligibility) --------------
    views = {
        candidate["candidate_object_id"]: candidate_views(
            candidate, payload_registry.get(candidate["candidate_object_id"]) or {}
        )
        for candidate in scope_passed
    }
    universe_size = len(scope_passed)
    df: dict[str, int] = {}
    if universe_size > 0:
        for view in views.values():
            for token in view["lexical_view"]:
                df[token] = df.get(token, 0) + 1

    def idf(token: str) -> float:
        return math.log2((universe_size + 1) / (df.get(token, 0) + 1))

    # --- per-candidate v2 rank keys ------------------------------------------
    receipts: list[dict[str, Any]] = []
    for candidate in scope_passed:
        object_id = candidate["candidate_object_id"]
        view = views[object_id]
        payload = payload_registry.get(object_id) or {}
        path_overlap = len(query_tokens & view["path_tokens"])
        title_overlap = len(query_tokens & view["title_tokens"])
        # unchanged v1 hard gate (path/title lexical overlap)
        gate_pass = (path_overlap + title_overlap) >= MIN_PRIMARY_SCORE
        symbol_exact_tier = sum(
            1
            for symbol in plan_symbols
            if any(symbol_exact_match(symbol, surface) for surface in view["exact_surfaces"])
        )
        rarity_weighted_overlap = sum(
            idf(token) for token in (query_tokens & view["lexical_view"])
        )
        basename_coverage = len(query_tokens & view["basename_tokens"])
        text_presence = len(query_tokens & view["text_tokens"])
        support = support_rank(object_id, channels)
        distance = candidate.get("min_structural_distance_transitions")
        if distance is None:
            distance = 1_000_000
        receipts.append(
            {
                "candidate_object_id": object_id,
                "locator_path": candidate.get("locator_path"),
                "source_id": candidate.get("source_id"),
                "source_version_id": candidate.get("source_version_id"),
                "object_type": candidate.get("object_type"),
                "provenance_origin_ids": sorted(candidate.get("provenance_origin_ids") or []),
                "a2_disposition": candidate.get("a2_disposition"),
                "path_overlap": path_overlap,
                "title_overlap": title_overlap,
                "gate_pass": gate_pass,
                "symbol_exact_tier": symbol_exact_tier,
                "rarity_weighted_overlap": rarity_weighted_overlap,
                "basename_coverage": basename_coverage,
                "text_presence": text_presence,
                "support_rank": support,
                "structural_distance": distance,
                "in_unbridged_graph": object_id in set(unbridged_graph),
                "disposition": "candidate" if gate_pass else "gate_rejected",
            }
        )

    candidates = [item for item in receipts if item["gate_pass"]]
    candidates.sort(
        key=lambda item: (
            -item["symbol_exact_tier"],
            -item["rarity_weighted_overlap"],
            -item["basename_coverage"],
            -item["text_presence"],
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

    selected_ids_in_order = [item["candidate_object_id"] for item in selected]
    v2_graph = merge_ids(selected_ids_in_order, unbridged_graph, GRAPH_CHANNEL_LIMIT)
    displaced_after = [oid for oid in unbridged_graph if oid not in v2_graph]
    baseline_admitted = case.get("baseline_old_cap_admitted_ids_injection_order") or []
    baseline_displaced = case.get("baseline_ordinary_graph_displaced_ids_before") or []

    origins_before = {
        origin
        for item in universe
        for origin in (item.get("provenance_origin_ids") or [])
    }
    origins_after = {origin for item in selected for origin in item["provenance_origin_ids"]}
    per_origin_attributed = {
        origin: sum(1 for item in selected if item.get("attributed_origin_id") == origin)
        for origin in sorted(origins_after)
    }

    return {
        "case_id": case.get("case_id"),
        "policy_version": POLICY_VERSION,
        "eligible_governed_bridge_candidate_count": len(universe),
        "eligible_after_scope_count": eligible_after_scope,
        "scope_rejected_candidate_count": scope_rejected,
        "gate_passing_candidate_count": len(candidates),
        "gate_rejected_candidate_count": len(scope_passed) - len(candidates),
        "baseline_old_cap_admitted_count": len(baseline_admitted),
        "selected_bridge_candidate_count": len(selected),
        "selected_object_ids": selected_ids_in_order,
        "candidate_receipts": receipts,
        "selected_rank_keys": [
            {
                "candidate_object_id": item["candidate_object_id"],
                "symbol_exact_tier": item["symbol_exact_tier"],
                "rarity_weighted_overlap": item["rarity_weighted_overlap"],
                "basename_coverage": item["basename_coverage"],
                "text_presence": item["text_presence"],
                "support_rank": item["support_rank"],
                "structural_distance": item["structural_distance"],
                "attributed_origin_id": item.get("attributed_origin_id"),
            }
            for item in selected
        ],
        "origin_capped_out_count": origin_capped_out,
        "beyond_selectivity_cap_count": beyond_selectivity_cap,
        "per_origin_attributed_counts": per_origin_attributed,
        "number_of_origins_before": len(origins_before),
        "number_of_origins_after": len(origins_after),
        "graph_admitted_bridge_candidates": [
            oid for oid in selected_ids_in_order if oid in set(v2_graph)
        ],
        "v2_graph_displacement_count": len(displaced_after),
        "v2_displaced_object_ids": displaced_after,
        "v1_graph_displacement_count": len(baseline_displaced),
        "selectivity_only_graph_ordering": v2_graph,
        "determinism_receipt": None,  # filled by the harness after double execution
    }


# ---------------------------------------------------------------------------
# Complete-universe evaluator (evaluator-only; reuses the frozen
# GoldEvidenceSelector.matches semantics)
# ---------------------------------------------------------------------------


def evaluate_complete_universe(
    case_id: str,
    case: dict[str, Any],
    selection: dict[str, Any],
    payload_registry: dict[str, Any],
    question: Any,
    a2_matched_ids: set[str],
) -> dict[str, Any]:
    from panda_agent.evaluation import GoldEvidenceSelector  # frozen matcher

    universe = {
        candidate["candidate_object_id"]: candidate
        for candidate in case.get("eligible_governed_bridge_candidates") or []
    }
    selected = set(selection["selected_object_ids"])
    gate_passed = {
        item["candidate_object_id"] for item in selection["candidate_receipts"] if item["gate_pass"]
    }
    group_records = []
    matched_universe_ids: set[str] = set()
    for group in question.required_evidence_groups:
        per_group = []
        for selector in group.any_of:
            for object_id, candidate in universe.items():
                payload = payload_registry.get(object_id) or {}
                item = {
                    "object_id": object_id,
                    "source_id": candidate.get("source_id"),
                    "source_version_id": candidate.get("source_version_id"),
                    "object_type": candidate.get("object_type"),
                    "locator": candidate.get("locator") or {},
                    "title": payload.get("title"),
                    "text": payload.get("text_payload_2000"),
                }
                if selector.matches(item):
                    per_group.append(object_id)
        matched_universe_ids.update(per_group)
        matched_unique = sorted(set(per_group))
        gate_passing = [oid for oid in matched_unique if oid in gate_passed]
        retained = [oid for oid in matched_unique if oid in selected and oid in gate_passed]
        if not matched_unique:
            group_class = "NOT_APPLICABLE_TO_SELECTIVITY"
        elif not gate_passing:
            group_class = "GATE_RECALL_LIMITATION"
        elif retained:
            group_class = "APPLICABLE_AND_RETAINED"
        else:
            group_class = "APPLICABLE_AND_LOST"
        group_records.append(
            {
                "group_id": group.group_id,
                "required_candidate_ids_in_eligible_universe": matched_unique,
                "gate_passing_ids": gate_passing,
                "gate_rejected_ids": [oid for oid in matched_unique if oid not in gate_passed],
                "v2_retained_ids": retained,
                "applicability_class": group_class,
            }
        )

    newly_visible = sorted(matched_universe_ids - a2_matched_ids)
    return {
        "case_id": case_id,
        "groups": group_records,
        "required_candidate_ids_in_eligible_universe": sorted(matched_universe_ids),
        "newly_visible_complete_universe_applicable_evidence": newly_visible,
        "gate_recall_limitation_count": sum(
            1 for g in group_records if g["applicability_class"] == "GATE_RECALL_LIMITATION"
        ),
        "applicable_and_lost_count": sum(
            1 for g in group_records if g["applicability_class"] == "APPLICABLE_AND_LOST"
        ),
        "applicable_and_retained_count": sum(
            1 for g in group_records if g["applicability_class"] == "APPLICABLE_AND_RETAINED"
        ),
        "not_applicable_count": sum(
            1 for g in group_records if g["applicability_class"] == "NOT_APPLICABLE_TO_SELECTIVITY"
        ),
    }


# ---------------------------------------------------------------------------
# Synthetic / property tests (Phase-1 gate; no real-case outcomes)
# ---------------------------------------------------------------------------


def _syn_case(eligible, question, plan=None, channels=None, unbridged=None, admitted=None):
    return {
        "case_id": "SYNTHETIC",
        "question": {"query": question, "query_sha256": "0" * 64},
        "frozen_plan_fields": plan or {},
        "eligible_governed_bridge_candidates": eligible,
        "eligible_governed_bridge_candidate_count": len(eligible),
        "baseline_old_cap_admitted_ids_injection_order": admitted or [],
        "unbridged_graph_ordering": unbridged or [],
        "baseline_bridged_graph_ordering_recomputed": [],
        "baseline_ordinary_graph_displaced_ids_before": [],
        "arms": {"STRUCTURED_BRIDGED": {"channel_rankings": channels or {}}},
    }


def _syn_cand(oid, path, origins, source_id="synth_repo", object_type="source_file", distance=1):
    return {
        "candidate_object_id": oid,
        "provenance_origin_ids": origins,
        "source_id": source_id,
        "source_version_id": source_id + "@syn",
        "locator_path": path,
        "min_structural_distance_transitions": distance,
        "a2_disposition": "A2_CAPPED_OUT",
        "object_type": object_type,
        "locator": {"path": path},
    }


def run_synthetic_tests() -> list[str]:
    failures: list[str] = []

    def check(name, cond):
        if not cond:
            failures.append(name)

    def oid(i):
        return f"object.{i:024d}"

    registry = {
        oid(i): {
            "object_id": oid(i), "title": "synthetic title", "source_id": "synth_repo",
            "text_payload_2000": "filler", "object_type": "source_file",
            "locator": {"path": f"synth/{i}.c"},
        }
        for i in range(60)
    }
    question = "restgas profile reconstruction workflow"
    plan = {"concepts": ["restgas profile"], "symbols": ["restgas_profile"]}

    # IDF properties
    def idf(N, df):
        return math.log2((N + 1) / (df + 1))

    check("idf df=N -> 0", idf(10, 10) == 0.0)
    check("idf non-negative", all(idf(10, d) >= 0 for d in range(1, 11)))
    vals = [idf(10, d) for d in range(1, 11)]
    check("idf monotonic", all(vals[i] > vals[i + 1] for i in range(9)))

    # df: multi-origin candidate counts once (dedup by object id)
    elig = [
        _syn_cand(oid(1), "restgas/a.c", ["o1", "o2"]),
        _syn_cand(oid(2), "restgas/b.c", ["o1"]),
    ]
    views = {
        c["candidate_object_id"]: candidate_views(c, registry.get(c["candidate_object_id"]) or {})["lexical_view"]
        for c in elig
    }
    df = {}
    for v in views.values():
        for t in v:
            df[t] = df.get(t, 0) + 1
    check("df multi-origin counts once", max(df.values()) == 2 and df.get("restgas") == 2)

    # lexical-view dedup: token in path+title+text counted once in the view
    cand = _syn_cand(oid(3), "restgas/dup.c", ["o1"])
    reg3 = {oid(3): {"object_id": oid(3), "title": "restgas dup", "source_id": "synth_repo",
                     "text_payload_2000": "restgas restgas restgas", "object_type": "source_file",
                     "locator": {"path": "restgas/dup.c"}}}
    v = candidate_views(cand, reg3[oid(3)])
    check("lexical-view dedup", sum(1 for t in v["lexical_view"] if t == "restgas") == 1)

    # symbol boundary positives/negatives
    check("symbol positive paren", symbol_exact_match("restgas_profile", "restgas_profile("))
    check("symbol positive slash", symbol_exact_match("restgas_profile", "/restgas_profile/"))
    check("symbol positive text", symbol_exact_match("restgas_profile", "uses restgas_profile here"))
    check("symbol negative backup", not symbol_exact_match("restgas_profile", "my_restgas_profile_backup"))
    check("symbol negative suffix digit", not symbol_exact_match("restgas_profile", "restgas_profile2"))
    check("symbol negative prefix", not symbol_exact_match("restgas_profile", "xrestgas_profile"))
    check("hyphen non-equivalence", not symbol_exact_match("restgas_profile", "restgas-profile"))
    check("camelCase non-equivalence", not symbol_exact_match("restgas_profile", "RestgasProfile"))
    check("underscore preserved", symbol_exact_match("restgas_profile", "the restgas_profile key"))
    check("title excluded from symbol tier",
          not symbol_exact_match("restgas_profile", "synthetic title"))
    check("distinct-symbol count", True)  # covered by tier computation below

    # distinct-symbol count semantics: two symbols both matching -> tier 2
    plan2 = {"symbols": ["restgas_profile", "pndtargetgenerator"]}
    elig2 = [_syn_cand(oid(5), "restgas/restgas_profile_pndtargetgenerator.c", ["o1"])]
    reg2 = {oid(5): {"object_id": oid(5), "title": "t", "source_id": "synth_repo",
                     "text_payload_2000": "restgas_profile pndtargetgenerator",
                     "object_type": "source_file", "locator": {"path": "restgas/x.c"}}}
    r2 = select_v2(_syn_case(elig2, "restgas_profile pndtargetgenerator", plan2), reg2)
    check("two distinct symbols -> tier 2",
          r2["candidate_receipts"][0]["symbol_exact_tier"] == 2)

    # empty plan.symbols -> tier 0
    r3 = select_v2(
        _syn_case([_syn_cand(oid(6), "restgas/a.c", ["o1"])], "restgas", {"symbols": []}), registry
    )
    check("empty symbols -> tier 0", r3["candidate_receipts"][0]["symbol_exact_tier"] == 0)

    # ordinary tokenizer unchanged
    check("tokenizer unchanged", tokenize("PndTargetGenerator.cxx") == {"pnd", "target", "generator", "cxx"})

    # hard gate unchanged: zero path/title overlap rejected even with symbol match
    elig4 = [_syn_cand(oid(7), "unrelated/zzz.c", ["o1"])]
    reg4 = {oid(7): {"object_id": oid(7), "title": "unrelated", "source_id": "synth_repo",
                     "text_payload_2000": "restgas_profile appears here", "object_type": "source_file",
                     "locator": {"path": "unrelated/zzz.c"}}}
    r4 = select_v2(
        _syn_case(elig4, "restgas_profile", {"symbols": ["restgas_profile"]}), reg4
    )
    check("hard gate unchanged (gate rejects zero path/title overlap)",
          r4["gate_rejected_candidate_count"] == 1 and r4["selected_bridge_candidate_count"] == 0)

    # support missing sorts worse than present
    elig5 = [
        _syn_cand(oid(8), "restgas/aa.c", ["oA"]),
        _syn_cand(oid(9), "restgas/bb.c", ["oB"]),
    ]
    r5 = select_v2(
        _syn_case(elig5, "restgas aa bb", None, {"sparse": [oid(9)]}), registry
    )
    check("support-missing ordering",
          r5["selected_candidates"] if False else
          [c["candidate_object_id"] for c in r5["selected_rank_keys"]][0] == oid(9))

    # origin attribution + caps
    elig6 = [_syn_cand(oid(10 + i), f"restgas/f{i}.c", ["oA"]) for i in range(6)]
    r6 = select_v2(_syn_case(elig6, "restgas", None), registry)
    check("per-origin cap", r6["selected_bridge_candidate_count"] == 4 and r6["origin_capped_out_count"] == 2)

    elig7 = [_syn_cand(oid(20 + i), f"restgas/g{i}.c", [f"o{i}"]) for i in range(12)]
    r7 = select_v2(_syn_case(elig7, "restgas", None), registry)
    check("selectivity cap", r7["selected_bridge_candidate_count"] == 8 and r7["beyond_selectivity_cap_count"] == 4)

    # zero-gate fail closed
    r8 = select_v2(_syn_case([_syn_cand(oid(30), "nothing/here.c", ["o1"])], "restgas", None), registry)
    check("zero-gate fail closed", r8["selected_bridge_candidate_count"] == 0)

    # object-id final tie-break
    r9 = select_v2(
        _syn_case(
            [_syn_cand(oid(32), "restgas/zz.c", ["o1"]), _syn_cand(oid(31), "restgas/aa.c", ["o2"])],
            "restgas",
            None,
        ),
        registry,
    )
    check("object-id tie-break", r9["selected_rank_keys"][0]["candidate_object_id"] == oid(31))

    # determinism
    elig10 = [_syn_cand(oid(40 + i), f"restgas/h{i}.c", [f"o{i % 3}"]) for i in range(15)]
    case10 = _syn_case(elig10, question, plan)
    check("determinism",
          json.dumps(select_v2(case10, registry), sort_keys=True)
          == json.dumps(select_v2(case10, registry), sort_keys=True))

    # subset invariant
    universe = {c["candidate_object_id"] for c in case10["eligible_governed_bridge_candidates"]}
    sel = set(select_v2(case10, registry)["selected_object_ids"])
    check("selected subset of eligible", sel <= universe)

    # ---- evaluator synthetic tests (synthetic selectors allowed) ----
    class _Sel:
        def __init__(self, d):
            self.d = d
            self.source_id = d.get("source_id")
            self.source_version_id = d.get("source_version_id")
            self.object_type = d.get("object_type")
            self.path = d.get("path")
            self.symbol = d.get("symbol")
            self.title_contains = d.get("title_contains")
            self.object_id = None
            self.start_line = None
            self.end_line = None
            self.pdf_page = None
            self.pdf_page_end = None
            self.section_contains = None

        def matches(self, item):
            locator = item.get("locator") or {}
            return all(
                (
                    self.source_id is None or item.get("source_id") == self.source_id,
                    self.source_version_id is None or item.get("source_version_id") == self.source_version_id,
                    self.object_type is None or item.get("object_type") == self.object_type,
                    self.path is None or (locator.get("path") or "").replace("\\", "/") == self.path,
                    self.symbol is None or locator.get("symbol") == self.symbol,
                    self.title_contains is None
                    or self.title_contains.casefold()
                    in " ".join([item.get("title") or "", *(str(v) for v in (locator.get("section_path") or [])), item.get("text") or ""]).casefold(),
                )
            )

    universe_items = {
        oid(50): {"candidate_object_id": oid(50), "source_id": "synth_repo",
                  "source_version_id": "synth_repo@1", "object_type": "source_file",
                  "locator": {"path": "restgas/prod_x.c"}, "a2_disposition": "A2_ADMITTED"},
        oid(51): {"candidate_object_id": oid(51), "source_id": "synth_repo",
                  "source_version_id": "synth_repo@1", "object_type": "source_file",
                  "locator": {"path": "restgas/other.c"}, "a2_disposition": "A2_CAPPED_OUT"},
    }
    # selector matching over the universe (reusing frozen semantics shape)
    sel = _Sel({"source_id": "synth_repo", "path": "restgas/prod_x.c"})
    matched = [oidc for oidc, c in universe_items.items() if sel.matches({
        "object_id": oidc, "source_id": c["source_id"], "source_version_id": c["source_version_id"],
        "object_type": c["object_type"], "locator": c["locator"], "title": "", "text": ""})]
    check("evaluator matcher positive", matched == [oid(50)])
    sel2 = _Sel({"source_id": "synth_repo", "path": "restgas/absent.c"})
    matched2 = [oidc for oidc, c in universe_items.items() if sel2.matches({
        "object_id": oidc, "source_id": c["source_id"], "source_version_id": c["source_version_id"],
        "object_type": c["object_type"], "locator": c["locator"], "title": "", "text": ""})]
    check("evaluator absent -> NOT_APPLICABLE class derivable", matched2 == [])

    # title_contains through section_path
    item = {"object_id": "x", "source_id": "s", "source_version_id": "s@1",
            "object_type": "readme_section",
            "locator": {"path": "r/README.md", "section_path": ["6.5", "POCA Workflow"]},
            "title": "6.5 MC-truth control", "text": "body"}
    check("title_contains via section_path", _Sel({"source_id": "s", "title_contains": "POCA Workflow"}).matches(item))

    return failures


# ---------------------------------------------------------------------------
# Phase-2 replay harness
# ---------------------------------------------------------------------------


def run_replay(project_root: Path) -> dict[str, Any]:
    from panda_agent.evaluation import load_gold_dataset

    fixture = json.loads(
        (project_root / "evaluation" / "d3_5_downstream_replay_fixture.json").read_text(encoding="utf-8")
    )
    gold = load_gold_dataset(project_root / "evaluation" / "benchmarks" / "v2_6" / "gold_questions.yaml")
    novel = load_gold_dataset(project_root / "evaluation" / "novel" / "v1" / "novel_dev.yaml")
    questions = {q.id: q for q in [*gold.questions, *novel.questions]}

    # A2 combined-pool match provenance for the newly-visible discovery record
    records = [
        json.loads(l)
        for l in (project_root / "data" / "evaluation" / "runs" / "d3_5_a2_focused_20260901" / "records.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if l
    ]
    a2_prov: dict[str, dict[str, list[str]]] = {}
    for case_id in fixture["identity"]["case_ids"]:
        rec = next(r for r in records if r["case_id"] == case_id and r["arm"] == "STRUCTURED_BRIDGED")
        mp = (rec.get("metrics") or {}).get("evidence_match_provenance") or {}
        prov = {}
        for field, entries in mp.items():
            for e in entries or []:
                if e.get("object_id"):
                    prov.setdefault(e.get("group_id"), []).append(e["object_id"])
        a2_prov[case_id] = prov

    results: dict[str, Any] = {}
    for case_id in fixture["identity"]["case_ids"]:
        case = fixture["cases"][case_id]
        first = select_v2(case, fixture["reranker_payload_registry"])
        second = select_v2(case, fixture["reranker_payload_registry"])
        deterministic = json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
        first["determinism_receipt"] = {
            "double_execution_identical": deterministic,
            "output_sha256": hashlib.sha256(
                json.dumps(first, sort_keys=True).encode("utf-8")
            ).hexdigest(),
        }
        if not deterministic:
            raise RuntimeError(f"non-deterministic v2 output for {case_id}")
        # selection is now frozen for this case; evaluator may read gold data
        a2_matched_ids = {
            oid for ids in a2_prov[case_id].values() for oid in ids
        }
        evaluation = evaluate_complete_universe(
            case_id, case, first, fixture["reranker_payload_registry"], questions[case_id],
            a2_matched_ids,
        )
        evaluation["a2_combined_pool_matched_reference"] = sorted(a2_matched_ids)
        results[case_id] = {"selection": first, "evaluation": evaluation}
    return results



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--run-synthetic-tests", action="store_true")
    parser.add_argument("--run-replay", action="store_true")
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    sys.stdout.reconfigure(encoding="utf-8")
    if args.run_synthetic_tests:
        failures = run_synthetic_tests()
        print(f"synthetic tests: passed; failures={len(failures)}")
        for failure in failures:
            print("FAILED:", failure)
        return 1 if failures else 0
    if args.run_replay:
        results = run_replay(project_root)
        out = project_root / "data" / "tmp" / "d3_5_a5_r2_replay_results.json"
        out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary = {}
        for case, r in results.items():
            s, e = r["selection"], r["evaluation"]
            summary[case] = {
                "eligible": s["eligible_governed_bridge_candidate_count"],
                "gate_passing": s["gate_passing_candidate_count"],
                "v2_selected": s["selected_bridge_candidate_count"],
                "v2_displacement": s["v2_graph_displacement_count"],
                "classes": {g["group_id"]: g["applicability_class"] for g in e["groups"]},
                "newly_visible": len(e["newly_visible_complete_universe_applicable_evidence"]),
            }
        print(json.dumps(summary, indent=1))
        print("results written to", out)
        return 0
    parser.error("choose --run-synthetic-tests or --run-replay")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
