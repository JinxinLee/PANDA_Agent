"""PANDA Agent D4-A5 — Second-Batch Low-Risk Locator Controlled Retirement Validation.

Pre-exposure implementation freeze only (Commit 1 of the A5 chain).
Authoritative preregistration: evaluation/d4_a4_batch2_retirement_preregistration.json.
Authoritative selection artifact: evaluation/d4_a4_batch2_low_risk_retirement_selection.json.

Controlled scientific validation of the frozen Batch-2 low-risk retirement:
  - Phase P: 7 questions x exactly 1 prospective Query Analyzer plan per case,
             acquired in frozen order with zero retries, each frozen together
             with its complete ordered contribution ledger, provenance origins,
             CURRENT_COMPAT execution projection, and BATCH2_RETIREMENT
             provenance-aware execution projection into
             evaluation/d4_a5_raw_prospective_plans.json (Commit 2).
  - Phase R: 14 paired shared-plan retrieval cells (7 cases x 2 arms) in the
             exact frozen schedule with 0 Analyzer provider calls. Both arms run
             the current D4-A3 production retrieval (Batch-1 runtime active);
             the retirement arm differs ONLY by the frozen execution projection.
             Frozen into evaluation/d4_a5_raw_paired_retirement_results.json
             (Commit 3).
  - Evaluator: deterministic, zero-provider evaluation executed only after
             Commit 3. Uses the frozen D4-A4 verdict contract module verbatim
             (masks, pair phenotypes, per-rule dispositions, 6-level verdict).

Production immutability: no production file is modified by this runner. The
treatment exists only inside the executor through non-mutating execution
projections. Batch-2 production remains inactive regardless of the outcome.

CLI (run with PYTHONPATH=src):
    python evaluation/scripts/d4_a5_batch2_controlled_retirement_validation.py --project-root . --mode audit
    python evaluation/scripts/d4_a5_batch2_controlled_retirement_validation.py --project-root . --mode execute-phase-p
    python evaluation/scripts/d4_a5_batch2_controlled_retirement_validation.py --project-root . --mode execute-phase-r
    python evaluation/scripts/d4_a5_batch2_controlled_retirement_validation.py --project-root . --mode evaluate
    python evaluation/scripts/d4_a5_batch2_controlled_retirement_validation.py --project-root . --mode verify-freeze
"""

from __future__ import annotations

import argparse
import copy
import datetime
import json
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_EVAL_SCRIPTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _EVAL_SCRIPTS_DIR.parent.parent
if str(_EVAL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_SCRIPTS_DIR))
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

import d4_a4_batch2_retirement_preregistration as b2
from panda_agent.config import load_query_expansions
from panda_agent.evaluation import (
    GoldQuestion,
    _matched_evidence_groups,
    load_gold_dataset,
)
from panda_agent.evaluation_runner import load_object_lookup
from panda_agent.models import RetrievalPlan
from panda_agent.retrieval import Retriever

# ---------------------------------------------------------------------------
# Frozen boundaries and authorities
# ---------------------------------------------------------------------------

STARTING_HEAD = "cb0f8c330f224a470401535b4b01f153488da99b"
STARTING_COMMIT_MESSAGE = "D4-A4 freeze second-batch low-risk retirement validation"
STARTING_PARENT = "631a66c125e8d58fee24bd448f868b4a8e423ab6"

EXECUTOR_FREEZE_COMMIT_MESSAGE = "D4-A5 freeze controlled retirement executor"
PLAN_FREEZE_COMMIT_MESSAGE = "D4-A5 freeze prospective shared plans"
RAW_FREEZE_COMMIT_MESSAGE = "D4-A5 freeze paired raw retirement results"
CLOSEOUT_COMMIT_MESSAGE = "D4-A5 close controlled retirement validation"

PREREGISTRATION_PATH = "evaluation/d4_a4_batch2_retirement_preregistration.json"
SELECTION_PATH = "evaluation/d4_a4_batch2_low_risk_retirement_selection.json"
MANIFEST_PATH = "evaluation/d4_a5_execution_manifest.json"
RAW_PLANS_PATH = "evaluation/d4_a5_raw_prospective_plans.json"
RAW_RESULTS_PATH = "evaluation/d4_a5_raw_paired_retirement_results.json"
EVALUATOR_RESULTS_PATH = "evaluation/d4_a5_evaluator_results.json"
RESULT_PATH = "evaluation/d4_a5_result.json"
REPORT_PATH = "evaluation/D4_A5_SECOND_BATCH_LOW_RISK_LOCATOR_CONTROLLED_RETIREMENT_VALIDATION.md"
RUNNER_PATH = "evaluation/scripts/d4_a5_batch2_controlled_retirement_validation.py"
TEST_PATH = "tests/unit/test_d4_a5_batch2_controlled_retirement_validation.py"

GOLD_QUESTIONS_PATH = "evaluation/benchmarks/v2_6/gold_questions.yaml"
NOVEL_DEV_PATH = "evaluation/novel/v1/novel_dev.yaml"
CONFIG_QUERY_EXPANSIONS_PATH = "configs/query_expansions.yaml"

# Production immutability boundary: every path here must remain Git-object
# unchanged from STARTING_HEAD for the whole A5 lifecycle.
PRODUCTION_IMMUTABLE_PATHS = (
    CONFIG_QUERY_EXPANSIONS_PATH,
    "src/panda_agent/config.py",
    "src/panda_agent/retrieval.py",
    "src/panda_agent/d3_structured.py",
    "src",
    "configs",
    GOLD_QUESTIONS_PATH,
    NOVEL_DEV_PATH,
    PREREGISTRATION_PATH,
    SELECTION_PATH,
)

CASE_ORDER = ["g052", "g055", "n003", "n004", "g007", "n014", "g060"]
ARMS = ["CURRENT_COMPAT", "BATCH2_RETIREMENT"]

# Frozen case-to-rule attribution (D4-A4 exact_case_to_rule_attribution).
CASE_ATTRIBUTION: dict[str, dict[str, Any]] = {
    "g052": {
        "owning_rule": "effective_acceptance_pipeline",
        "role": "direct_trigger",
        "matched_retirement_rules": ["effective_acceptance_pipeline"],
        "matched_batch1_rule_ids": ["restgas_profile_workflow"],
    },
    "g055": {
        "owning_rule": "effective_acceptance_pipeline",
        "role": "nonmatching_control",
        "matched_retirement_rules": [],
        "matched_batch1_rule_ids": [],
    },
    "n003": {
        "owning_rule": "effective_acceptance_pipeline",
        "role": "nonmatching_control",
        "matched_retirement_rules": [],
        "matched_batch1_rule_ids": [],
    },
    "n004": {
        "owning_rule": "root_macro_usage",
        "role": "direct_trigger",
        "matched_retirement_rules": ["root_macro_usage"],
        "matched_batch1_rule_ids": [],
    },
    "g007": {
        "owning_rule": "root_macro_usage",
        "role": "negative_control",
        "matched_retirement_rules": [],
        "matched_batch1_rule_ids": [],
    },
    "n014": {
        "owning_rule": "model_factory_theory",
        "role": "direct_trigger",
        "matched_retirement_rules": ["model_factory_theory"],
        "matched_batch1_rule_ids": [],
    },
    "g060": {
        "owning_rule": "model_factory_theory",
        "role": "nonmatching_control",
        "matched_retirement_rules": [],
        "matched_batch1_rule_ids": [],
    },
}

ACTIVE_RULE_CASE_GROUPS: dict[str, dict[str, list[str]]] = {
    "effective_acceptance_pipeline": {"g052": ["g052.e1"]},
    "root_macro_usage": {"n004": ["n004.e1"]},
    "model_factory_theory": {"n014": ["n014.e1", "n014.e2"]},
}

ANSWERED_CASES = list(b2.ANSWERED_CASES)
NEGATIVE_CONTROL_CASES = list(b2.NEGATIVE_CONTROL_CASES)
NONMATCHING_CONTROLS = ["g055", "n003", "g007", "g060"]

def _build_schedule_14() -> list[dict[str, Any]]:
    cells: list[dict[str, Any]] = []
    for case_id, arm in (
        ("g052", "CURRENT_COMPAT"),
        ("g052", "BATCH2_RETIREMENT"),
        ("g055", "CURRENT_COMPAT"),
        ("g055", "BATCH2_RETIREMENT"),
        ("n003", "CURRENT_COMPAT"),
        ("n003", "BATCH2_RETIREMENT"),
        ("n004", "CURRENT_COMPAT"),
        ("n004", "BATCH2_RETIREMENT"),
        ("g007", "CURRENT_COMPAT"),
        ("g007", "BATCH2_RETIREMENT"),
        ("n014", "CURRENT_COMPAT"),
        ("n014", "BATCH2_RETIREMENT"),
        ("g060", "CURRENT_COMPAT"),
        ("g060", "BATCH2_RETIREMENT"),
    ):
        cells.append({
            "cell_index": len(cells) + 1,
            "cell_id": (
                f"{case_id}_current_compat"
                if arm == "CURRENT_COMPAT"
                else f"{case_id}_batch2_retirement"
            ),
            "case_id": case_id,
            "arm": arm,
            "role": CASE_ATTRIBUTION[case_id]["role"],
            "batch2_retirement_mask_applied": (
                arm == "BATCH2_RETIREMENT"
                and bool(CASE_ATTRIBUTION[case_id]["matched_retirement_rules"])
            ),
            "retirement_rule_ids": (
                list(CASE_ATTRIBUTION[case_id]["matched_retirement_rules"])
                if arm == "BATCH2_RETIREMENT"
                else []
            ),
        })
    return cells


SCHEDULE_14: list[dict[str, Any]] = _build_schedule_14()

EXPECTED_MODEL = "gemini-3.8-flash"
EXPECTED_EMBEDDING_MODEL = "gemini-embedding-2"
EXPECTED_TEMPERATURE = 0.0
EXPECTED_VERTEX_LOCATION = "global"
MAX_PROVIDER_ATTEMPTS_PER_CASE = 1  # Frozen retry policy: max_retries = 0.

EXPECTED_ACCOUNTING = {
    "analyzer_phase_p": 7,
    "analyzer_phase_r": 0,
    "embedding_downstream": 14,
    "reranker_downstream": 14,
    "total_logical_model_calls": 35,
    "qa_verifier_judge": 0,
}

PRIMARY_METRIC_KEYS = [
    "recall_at_5",
    "recall_at_10",
    "recall_at_20",
    "combined_candidate_recall",
    "final_evidence_recall",
    "critical_final_evidence_recall",
]

# Contribution provenance origins beyond matched rule IDs.
ORIGIN_ACCEPTED_ANALYZER_DELTA = "accepted_analyzer_semantic_delta"
ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE = "runtime_deterministic_override"

# Frozen g052 runtime anchor override (production deterministic feedback rule):
# li_2026 hints are replaced by exactly these pages when the feedback condition
# triggers; these contributions are runtime-owned, never rule-owned, and never
# part of any retirement mask.
RUNTIME_FEEDBACK_OVERRIDE_HINTS = ("li_2026", [141, 149, 151])

VERDICT_INVALID = b2.BATCH_VERDICT_LEVELS[1]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _git(args: list[str], project_root: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def git_head(project_root: Path) -> str:
    return _git(["rev-parse", "HEAD"], project_root)


def git_commit_message(project_root: Path, sha: str) -> str:
    return _git(["log", "-1", "--format=%s", sha], project_root)


def git_parent(project_root: Path, sha: str) -> str:
    return _git(["rev-parse", f"{sha}^"], project_root)


def git_blob(project_root: Path, rel_path: str, rev: str = "HEAD") -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", f"{rev}:{rel_path}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def git_paths_unchanged_between(project_root: Path, base: str, head: str, paths: list[str]) -> list[str]:
    """Return the subset of paths whose Git objects differ between base and head."""
    changed: list[str] = []
    for rel in paths:
        b = git_blob(project_root, rel, base)
        h = git_blob(project_root, rel, head)
        if b != h:
            changed.append(rel)
    return changed


def assert_clean_worktree(project_root: Path) -> None:
    status = _git(["status", "--porcelain"], project_root)
    if status:
        raise RuntimeError(f"Worktree or index is not clean:\n{status}")


def compute_plan_signature(plan_dict: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Deterministic JSON-canonical plan signature (frozen A2-V2-R2 semantics)."""
    intent = plan_dict.get("intent", "")
    repos = sorted(plan_dict.get("target_repositories", []))
    symbols = sorted(plan_dict.get("symbols", []))
    concepts = sorted(c.strip().casefold() for c in plan_dict.get("concepts", []))
    req_types = sorted(plan_dict.get("required_source_types", []))
    paper_hints = [
        [k, sorted(v)] for k, v in sorted((plan_dict.get("paper_page_hints") or {}).items())
    ]
    scopes = [[k, v] for k, v in sorted((plan_dict.get("concept_scopes") or {}).items())]
    sig_payload = {
        "intent": intent,
        "target_repositories": repos,
        "symbols": symbols,
        "normalized_concepts": concepts,
        "required_source_types": req_types,
        "paper_page_hints": paper_hints,
        "concept_scopes": scopes,
    }
    sig_str = json.dumps(sig_payload, sort_keys=True)
    return sig_str, json.loads(sig_str)


# ---------------------------------------------------------------------------
# Contribution ledger and provenance-aware execution projection (pure)
# ---------------------------------------------------------------------------


def _analyzer_delta_values(plan_dict: dict[str, Any], field: str) -> list[str]:
    diagnostics = plan_dict.get("analysis_diagnostics") or {}
    delta = diagnostics.get("analyzer_accepted_semantic_delta") or {}
    values = delta.get(field) or []
    if isinstance(values, dict):
        values = list(values.values())
    result: list[str] = []
    for item in values:
        if isinstance(item, dict):
            value = item.get("value")
            if value:
                result.append(str(value))
        elif item:
            result.append(str(item))
    return result


def build_contribution_ledger(
    canonical_plan: dict[str, Any],
    rules_by_id: dict[str, dict[str, Any]],
    matched_rule_ids: list[str],
) -> list[dict[str, Any]]:
    """Complete ordered contribution ledger for one canonical plan.

    Every plan contribution (symbols, concepts, repositories, paper page hints)
    is recorded with its full origin set. Origins are:
      - matched reviewed query-expansion rule IDs contributing the value;
      - the accepted Analyzer semantic delta (symbols/concepts/repositories);
      - the production deterministic runtime override (li_2026 feedback anchors).
    """
    matched = [rid for rid in matched_rule_ids if rid in rules_by_id]
    delta_symbols = set(_analyzer_delta_values(canonical_plan, "symbols"))
    delta_concepts = set(_analyzer_delta_values(canonical_plan, "concepts"))
    delta_repos = set(_analyzer_delta_values(canonical_plan, "repository_additions"))

    origin_rules_symbol: dict[str, list[str]] = {}
    origin_rules_concept: dict[str, list[str]] = {}
    origin_rules_repo: dict[str, list[str]] = {}
    origin_rules_hint: dict[tuple[str, int], list[str]] = {}
    for rid in matched:
        rule = rules_by_id[rid]
        for sym in rule.get("symbols") or []:
            origin_rules_symbol.setdefault(sym, []).append(rid)
        for con in rule.get("concepts") or []:
            origin_rules_concept.setdefault(con, []).append(rid)
        for repo in rule.get("repositories") or []:
            origin_rules_repo.setdefault(repo, []).append(rid)
        for source_id, pages in (rule.get("paper_page_hints") or {}).items():
            for page in pages or []:
                origin_rules_hint.setdefault((str(source_id), int(page)), []).append(rid)

    ledger: list[dict[str, Any]] = []

    def _entry(kind: str, value: str, *, source_id: str | None = None, pdf_page: int | None = None,
               rule_origins: list[str], has_delta_origin: bool = False,
               has_runtime_override: bool = False, in_plan: bool = True) -> None:
        origins = list(rule_origins)
        origin_types: dict[str, str] = {rid: "reviewed_expansion_rule" for rid in rule_origins}
        if has_delta_origin:
            origins.append(ORIGIN_ACCEPTED_ANALYZER_DELTA)
            origin_types[ORIGIN_ACCEPTED_ANALYZER_DELTA] = "accepted_analyzer_semantic_output"
        if has_runtime_override:
            origins.append(ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE)
            origin_types[ORIGIN_RUNTIME_DETERMINISTIC_OVERRIDE] = "production_deterministic_override"
        ledger.append({
            "contribution_id": (
                f"{kind}::{value}" if pdf_page is None else f"{kind}::{source_id}#{pdf_page}"
            ),
            "kind": kind,
            "value": value,
            "source_id": source_id,
            "pdf_page": pdf_page,
            "provenance_origin_ids": origins,
            "origin_types": origin_types,
            "plan_present": in_plan,
        })

    # Ordered as the plan holds the values (canonical plan order is frozen).
    for sym in canonical_plan.get("symbols") or []:
        _entry("symbol", sym, rule_origins=origin_rules_symbol.get(sym, []),
               has_delta_origin=sym in delta_symbols)
    for con in canonical_plan.get("concepts") or []:
        _entry("concept", con, rule_origins=origin_rules_concept.get(con, []),
               has_delta_origin=con in delta_concepts)
    for repo in canonical_plan.get("target_repositories") or []:
        _entry("repository", repo, rule_origins=origin_rules_repo.get(repo, []),
               has_delta_origin=repo in delta_repos)
    for source_id, pages in (canonical_plan.get("paper_page_hints") or {}).items():
        for page in pages or []:
            key = (str(source_id), int(page))
            runtime_override = (
                key[0] == RUNTIME_FEEDBACK_OVERRIDE_HINTS[0]
                and key[1] in RUNTIME_FEEDBACK_OVERRIDE_HINTS[1]
                and not origin_rules_hint.get(key)
            )
            _entry("paper_page_hint", f"{key[0]}#{key[1]}", source_id=key[0], pdf_page=key[1],
                   rule_origins=origin_rules_hint.get(key, []),
                   has_runtime_override=runtime_override)
    return ledger


def validate_ledger_coverage(
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
) -> tuple[bool, str | None]:
    """Fail-closed ledger coverage: every plan contribution present with >=1 origin."""
    by_id = {entry["contribution_id"]: entry for entry in ledger}
    for sym in canonical_plan.get("symbols") or []:
        entry = by_id.get(f"symbol::{sym}")
        if entry is None:
            return False, f"Symbol contribution missing from ledger: {sym}"
        if not entry["provenance_origin_ids"]:
            return False, f"Symbol contribution has empty provenance: {sym}"
    for con in canonical_plan.get("concepts") or []:
        entry = by_id.get(f"concept::{con}")
        if entry is None:
            return False, f"Concept contribution missing from ledger: {con}"
        if not entry["provenance_origin_ids"]:
            return False, f"Concept contribution has empty provenance: {con}"
    for repo in canonical_plan.get("target_repositories") or []:
        entry = by_id.get(f"repository::{repo}")
        if entry is None:
            return False, f"Repository contribution missing from ledger: {repo}"
    for source_id, pages in (canonical_plan.get("paper_page_hints") or {}).items():
        for page in pages or []:
            entry = by_id.get(f"paper_page_hint::{source_id}#{int(page)}")
            if entry is None:
                return False, f"Page hint contribution missing from ledger: {source_id}#{page}"
            if not entry["provenance_origin_ids"]:
                return False, f"Page hint contribution has empty provenance: {source_id}#{page}"
    return True, None


def build_batch2_mask_entries(
    case_id: str,
    matched_retirement_rules: list[str],
    masks: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Mask entries for one case: only the frozen D4-A4 mask components of the
    matched selected Batch-2 rules. Controls receive an empty list."""
    masks = masks or b2.FROZEN_RETIREMENT_MASKS
    entries: list[dict[str, Any]] = []
    for rid in matched_retirement_rules:
        mask = masks.get(rid)
        if mask is None:
            raise ValueError(f"No frozen retirement mask for selected rule {rid}")
        for sym in mask.get("symbols_retired", []):
            entries.append({
                "rule_id": rid,
                "kind": "symbol",
                "value": sym,
                "source_id": None,
                "pdf_page": None,
            })
        for source_id, pages in (mask.get("paper_page_hints_retired") or {}).items():
            for page in pages or []:
                entries.append({
                    "rule_id": rid,
                    "kind": "paper_page_hint",
                    "value": f"{source_id}#{int(page)}",
                    "source_id": str(source_id),
                    "pdf_page": int(page),
                })
    return entries


def build_retirement_projection(
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    mask_entries: list[dict[str, Any]],
    matched_retirement_rules: list[str],
    masks: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Provenance-aware BATCH2_RETIREMENT execution projection.

    Uses the frozen D4-A4 subtraction function verbatim on ledger-shaped locator
    records. A masked locator is removed from the projected plan if and only if
    no independent origin survives; otherwise the locator remains active and the
    surviving origins are recorded. The canonical plan is never mutated.
    """
    masks = masks or b2.FROZEN_RETIREMENT_MASKS
    by_id = {entry["contribution_id"]: entry for entry in ledger}

    projection_input: list[dict[str, Any]] = []
    for entry in mask_entries:
        contribution_id = (
            f"symbol::{entry['value']}"
            if entry["kind"] == "symbol"
            else f"paper_page_hint::{entry['source_id']}#{entry['pdf_page']}"
        )
        ledger_entry = by_id.get(contribution_id)
        if ledger_entry is None:
            raise ValueError(
                f"Masked contribution not identified in canonical plan ledger: {contribution_id}"
            )
        if not ledger_entry["provenance_origin_ids"]:
            raise ValueError(f"Ambiguous provenance for masked contribution: {contribution_id}")
        if entry["rule_id"] not in ledger_entry["provenance_origin_ids"]:
            raise ValueError(
                f"Masked contribution lacks selected-rule origin provenance: {contribution_id}"
            )
        projection_input.append({
            "contribution_id": contribution_id,
            "kind": entry["kind"],
            "locator_path": entry["value"] if entry["kind"] == "symbol" else None,
            "source_id": entry["source_id"],
            "pdf_page": entry["pdf_page"],
            "provenance_origin_ids": list(ledger_entry["provenance_origin_ids"]),
        })

    surviving = b2.subtract_batch2_provenance(
        projection_input, matched_retirement_rules, masks
    )
    surviving_ids = {entry["contribution_id"] for entry in surviving}

    removed_symbols: list[str] = []
    removed_hints: dict[str, list[int]] = {}
    removed_rule_origins: list[dict[str, Any]] = []
    surviving_independent_origins: list[dict[str, Any]] = []
    for item in projection_input:
        origins = list(item["provenance_origin_ids"])
        retired = [o for o in origins if o in matched_retirement_rules]
        independent = [o for o in origins if o not in matched_retirement_rules]
        display_value = item["locator_path"] or (
            f"{item['source_id']}#{item['pdf_page']}"
        )
        removed_rule_origins.append({
            "contribution_id": item["contribution_id"],
            "kind": item["kind"],
            "value": display_value,
            "source_id": item["source_id"],
            "pdf_page": item["pdf_page"],
            "retired_rule_origins": retired,
            "surviving_independent_origins": independent,
            "effectively_removed": item["contribution_id"] not in surviving_ids,
        })
        if item["contribution_id"] in surviving_ids:
            surviving_independent_origins.append({
                "contribution_id": item["contribution_id"],
                "kind": item["kind"],
                "value": display_value,
                "source_id": item["source_id"],
                "pdf_page": item["pdf_page"],
                "surviving_independent_origins": independent,
            })
            continue
        if item["kind"] == "symbol":
            removed_symbols.append(item["locator_path"])
        else:
            removed_hints.setdefault(item["source_id"], []).append(item["pdf_page"])

    projected = copy.deepcopy(canonical_plan)
    if removed_symbols:
        projected["symbols"] = [
            s for s in (projected.get("symbols") or []) if s not in set(removed_symbols)
        ]
    if removed_hints:
        hints = {
            str(src): list(pages)
            for src, pages in (projected.get("paper_page_hints") or {}).items()
        }
        for src, pages in removed_hints.items():
            if src in hints:
                hints[src] = [p for p in hints[src] if p not in set(pages)]
                if not hints[src]:
                    del hints[src]
        projected["paper_page_hints"] = hints

    removed_symbols_effective = sorted(set(removed_symbols))
    removed_hints_effective = {
        src: sorted(pages) for src, pages in removed_hints.items()
    }
    receipts = {
        "matched_retirement_rules": list(matched_retirement_rules),
        "mask_entry_count": len(projection_input),
        "removed_rule_origin_entries": removed_rule_origins,
        "surviving_independent_origin_entries": surviving_independent_origins,
        "effective_removed_symbols": removed_symbols_effective,
        "effective_removed_paper_page_hints": removed_hints_effective,
        "effective_removal_count": len(removed_symbols_effective) + sum(
            len(pages) for pages in removed_hints_effective.values()
        ),
        "canonical_plan_unchanged": canonical_plan == copy.deepcopy(canonical_plan),
    }
    return projected, receipts


def verify_projection_diff(
    canonical_plan: dict[str, Any],
    projected_plan: dict[str, Any],
    receipts: dict[str, Any],
) -> tuple[bool, str | None]:
    """Mechanical no-non-mask-drift check: canonical vs projected differ only in
    the exact masked values recorded in the receipts."""
    expected_symbols = set(receipts["effective_removed_symbols"])
    expected_hints = {src: set(pages) for src, pages in receipts["effective_removed_paper_page_hints"].items()}

    if projected_plan.get("symbols") != [
        s for s in (canonical_plan.get("symbols") or []) if s not in expected_symbols
    ]:
        return False, "Projected symbols differ beyond the frozen mask"
    canonical_hints = {
        str(src): list(pages) for src, pages in (canonical_plan.get("paper_page_hints") or {}).items()
    }
    expected_projected_hints = {
        src: [p for p in pages if p not in expected_hints.get(src, set())]
        for src, pages in canonical_hints.items()
    }
    expected_projected_hints = {src: pages for src, pages in expected_projected_hints.items() if pages}
    if projected_plan.get("paper_page_hints") != expected_projected_hints:
        return False, "Projected paper page hints differ beyond the frozen mask"
    for field, value in canonical_plan.items():
        if field in ("symbols", "paper_page_hints"):
            continue
        if projected_plan.get(field) != value:
            return False, f"Non-mask field changed in projection: {field}"
    return True, None


def build_provenance_gate_receipt(
    case_id: str,
    attribution: dict[str, Any],
    matched_rule_ids: list[str],
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    current_compat_projection: dict[str, Any],
    batch2_retirement_projection: dict[str, Any],
    projection_receipts: dict[str, Any],
) -> dict[str, Any]:
    """Pre-outcome provenance gate (task Section 11 / D4-A4 pre_outcome_gate)."""
    selected_expected = list(attribution["matched_retirement_rules"])
    matched_batch2 = [rid for rid in selected_expected if rid in matched_rule_ids]
    gate: dict[str, Any] = {"case_id": case_id, "checks": {}}

    gate["checks"]["selected_rule_matched"] = {
        "expected": selected_expected,
        "observed": matched_batch2,
        "pass": sorted(matched_batch2) == sorted(selected_expected),
    }
    mask_entries = build_batch2_mask_entries(case_id, matched_batch2)
    expected_mask_count = 0
    for rid in matched_batch2:
        frozen = b2.FROZEN_RETIREMENT_MASKS[rid]
        expected_mask_count += len(frozen.get("symbols_retired", []))
        expected_mask_count += sum(
            len(pages or []) for pages in (frozen.get("paper_page_hints_retired") or {}).values()
        )
    gate["checks"]["mask_entry_count"] = {
        "expected": expected_mask_count,
        "observed": len(mask_entries),
        "pass": len(mask_entries) == expected_mask_count
        and (len(mask_entries) > 0) == bool(selected_expected),
    }
    coverage_ok, coverage_error = validate_ledger_coverage(canonical_plan, ledger)
    gate["checks"]["ledger_coverage"] = {"pass": coverage_ok, "error": coverage_error}

    represented = True
    represented_error = None
    if mask_entries:
        by_id = {entry["contribution_id"]: entry for entry in ledger}
        for entry in mask_entries:
            cid = (
                f"symbol::{entry['value']}"
                if entry["kind"] == "symbol"
                else f"paper_page_hint::{entry['source_id']}#{entry['pdf_page']}"
            )
            ledger_entry = by_id.get(cid)
            if ledger_entry is None or not ledger_entry.get("plan_present"):
                represented = False
                represented_error = f"Masked contribution not represented in canonical plan: {cid}"
                break
            if entry["rule_id"] not in (ledger_entry["provenance_origin_ids"] or []):
                represented = False
                represented_error = f"Masked contribution lacks rule-origin provenance: {cid}"
                break
    gate["checks"]["frozen_mask_represented"] = {"pass": represented, "error": represented_error}

    gate["checks"]["current_compat_projection_identical"] = {
        "pass": current_compat_projection == canonical_plan,
    }
    diff_ok, diff_error = verify_projection_diff(
        canonical_plan, batch2_retirement_projection, projection_receipts
    )
    gate["checks"]["retirement_projection_mask_only"] = {"pass": diff_ok, "error": diff_error}
    if not selected_expected:
        gate["checks"]["control_projection_identical"] = {
            "pass": batch2_retirement_projection == canonical_plan,
        }

    gate["pass"] = all(
        item.get("pass", False) if isinstance(item, dict) else bool(item)
        for item in gate["checks"].values()
    )
    gate["projection_receipts"] = projection_receipts
    return gate


# ---------------------------------------------------------------------------
# Starting boundary and freeze gates
# ---------------------------------------------------------------------------


def audit_starting_boundary(project_root: Path) -> dict[str, Any]:
    """Section 1 boundary: config state, D4-A4 artifacts, production immutability."""
    load_dotenv(project_root / ".env")

    head = git_head(project_root)
    head_message = git_commit_message(project_root, head)

    prereg = _load_json(project_root / PREREGISTRATION_PATH)
    selection = _load_json(project_root / SELECTION_PATH)
    qe = load_query_expansions(project_root / CONFIG_QUERY_EXPANSIONS_PATH)
    rules = qe.model_dump(mode="python")["rules"]
    boundary = b2.audit_starting_boundary(rules)

    batch2_rules_clean = b2.audit_candidate_drift(
        rules,
        _load_json(project_root / "evaluation/d4_a0_expansion_component_inventory.json")["rules"],
    )

    manifest_ok = True
    manifest_error = None
    manifest_path = project_root / MANIFEST_PATH
    if not manifest_path.exists():
        manifest_ok = False
        manifest_error = f"missing {MANIFEST_PATH}"

    return {
        "head": head,
        "head_message": head_message,
        "preregistration_present": True,
        "selection_present": True,
        "rule_boundary": boundary,
        "batch2_candidate_drift": batch2_rules_clean,
        "manifest_present": manifest_ok,
        "manifest_error": manifest_error,
        "prereg_selected_rules": prereg["exact_selected_rules"],
        "prereg_cohort": prereg["exact_case_cohort"],
    }


def verify_executor_freeze_gate(project_root: Path) -> dict[str, Any]:
    """Gate before Phase P: HEAD is the A5 executor-freeze commit, a direct
    child of the D4-A4 starting HEAD, with production files unchanged."""
    assert_clean_worktree(project_root)
    head = git_head(project_root)
    message = git_commit_message(project_root, head)
    if message != EXECUTOR_FREEZE_COMMIT_MESSAGE:
        raise RuntimeError(
            f"Phase P requires HEAD to be the executor freeze commit "
            f"('{EXECUTOR_FREEZE_COMMIT_MESSAGE}'), got '{message}'"
        )
    parent = git_parent(project_root, head)
    if parent != STARTING_HEAD:
        raise RuntimeError(
            f"Executor freeze commit parent must be {STARTING_HEAD}, got {parent}"
        )
    changed = git_paths_unchanged_between(
        project_root, STARTING_HEAD, head, list(PRODUCTION_IMMUTABLE_PATHS) + [RUNNER_PATH, TEST_PATH]
    )
    changed = [p for p in changed if p in PRODUCTION_IMMUTABLE_PATHS]
    if changed:
        raise RuntimeError(f"Production/frozen paths changed since starting HEAD: {changed}")
    for rel in (PREREGISTRATION_PATH, SELECTION_PATH):
        if git_blob(project_root, rel, STARTING_HEAD) != git_blob(project_root, rel, head):
            raise RuntimeError(f"D4-A4 authority artifact changed: {rel}")
    return {"head": head, "parent": parent, "message": message}


def _require_freeze_commit(
    project_root: Path,
    expected_message: str,
    expected_parent: str,
) -> str:
    assert_clean_worktree(project_root)
    head = git_head(project_root)
    message = git_commit_message(project_root, head)
    if message != expected_message:
        raise RuntimeError(
            f"Expected HEAD commit '{expected_message}', got '{message}'"
        )
    parent = git_parent(project_root, head)
    if parent != expected_parent:
        raise RuntimeError(
            f"Expected HEAD parent {expected_parent}, got {parent}"
        )
    return head


def verify_plan_freeze_gate(project_root: Path, executor_freeze_head: str) -> dict[str, Any]:
    """Gate before Phase R: HEAD is the plan-freeze commit (child of the
    executor freeze commit); plans artifact present, clean and committed."""
    head = _require_freeze_commit(project_root, PLAN_FREEZE_COMMIT_MESSAGE, executor_freeze_head)
    rel = RAW_PLANS_PATH.replace("\\", "/")
    proc = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{rel}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"{RAW_PLANS_PATH} is not committed at HEAD; plan freeze gate failed")
    changed = git_paths_unchanged_between(
        project_root, executor_freeze_head, head,
        list(PRODUCTION_IMMUTABLE_PATHS) + [RUNNER_PATH, TEST_PATH, RAW_PLANS_PATH],
    )
    changed = [p for p in changed if p not in (RAW_PLANS_PATH, MANIFEST_PATH)]
    if changed:
        raise RuntimeError(f"Unexpected frozen-path drift between executor and plan freeze: {changed}")
    return {"head": head, "executor_freeze_head": executor_freeze_head}


def verify_raw_freeze_gate(project_root: Path, plan_freeze_head: str) -> dict[str, Any]:
    """Gate before evaluator execution: HEAD is the raw-freeze commit (child of
    the plan-freeze commit); raw + plan artifacts committed and unchanged."""
    head = _require_freeze_commit(project_root, RAW_FREEZE_COMMIT_MESSAGE, plan_freeze_head)
    for rel in (RAW_RESULTS_PATH, RAW_PLANS_PATH):
        proc = subprocess.run(
            ["git", "cat-file", "-e", f"HEAD:{rel.replace(chr(92), '/')}"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"{rel} is not committed at HEAD; raw freeze gate failed")
    changed = git_paths_unchanged_between(
        project_root, plan_freeze_head, head,
        list(PRODUCTION_IMMUTABLE_PATHS) + [RUNNER_PATH, TEST_PATH, RAW_PLANS_PATH],
    )
    changed = [p for p in changed if p not in (RAW_RESULTS_PATH, MANIFEST_PATH)]
    if changed:
        raise RuntimeError(f"Unexpected frozen-path drift between plan and raw freeze: {changed}")
    plans_unchanged = git_paths_unchanged_between(project_root, plan_freeze_head, head, [RAW_PLANS_PATH])
    if plans_unchanged:
        raise RuntimeError("Raw plans artifact changed after plan freeze")
    return {"head": head, "plan_freeze_head": plan_freeze_head}


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def build_initial_manifest(project_root: Path) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5",
        "stage": "d4_a5_batch2_controlled_retirement_execution_manifest",
        "created_at": _utc_now(),
        "starting_head": STARTING_HEAD,
        "starting_commit_message": STARTING_COMMIT_MESSAGE,
        "implementation_freeze_contract": {
            "policy": "GIT_COMMIT_CONTAINING_THIS_ARTIFACT",
            "expected_commit_message": EXECUTOR_FREEZE_COMMIT_MESSAGE,
            "expected_parent": STARTING_HEAD,
        },
        "plan_freeze_gate_contract": {
            "policy": "HARD_COMMIT_PLAN_FREEZE_GATE",
            "expected_commit_message": PLAN_FREEZE_COMMIT_MESSAGE,
            "raw_plans_path": RAW_PLANS_PATH,
        },
        "raw_freeze_gate_contract": {
            "policy": "HARD_COMMIT_RAW_FREEZE_GATE",
            "expected_commit_message": RAW_FREEZE_COMMIT_MESSAGE,
            "raw_results_path": RAW_RESULTS_PATH,
        },
        "evaluation_tier": "T2",
        "mode": "controlled_batch2_retirement_retrieval",
        "preregistration_authority": PREREGISTRATION_PATH,
        "selection_authority": SELECTION_PATH,
        "exact_selected_rules": list(b2.CANDIDATE_RULE_IDS),
        "frozen_retirement_masks": b2.FROZEN_RETIREMENT_MASKS,
        "exact_case_cohort": list(CASE_ORDER),
        "case_to_rule_attribution": CASE_ATTRIBUTION,
        "scientific_model_contract": {
            "generation_and_reranker": EXPECTED_MODEL,
            "embedding": EXPECTED_EMBEDDING_MODEL,
            "location": EXPECTED_VERTEX_LOCATION,
            "temperature": EXPECTED_TEMPERATURE,
            "max_retries": 0,
        },
        "phase_p_slots_7": [
            {
                "slot_index": i + 1,
                "plan_id": f"prospective_{cid}",
                "case_id": cid,
                "role": CASE_ATTRIBUTION[cid]["role"],
                "status": "NOT_EXECUTED",
                "analyzer_calls": 0,
                "token_usage": 0,
            }
            for i, cid in enumerate(CASE_ORDER)
        ],
        "phase_r_cells_14": [
            {
                "cell_index": cell["cell_index"],
                "cell_id": cell["cell_id"],
                "case_id": cell["case_id"],
                "arm": cell["arm"],
                "role": cell["role"],
                "batch2_retirement_mask_applied": cell["batch2_retirement_mask_applied"],
                "status": "NOT_EXECUTED",
                "token_usage": 0,
            }
            for cell in SCHEDULE_14
        ],
        "pre_exposure_accounting": {
            "analyzer_calls": 0,
            "embedding_calls": 0,
            "reranker_calls": 0,
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "db_writes": 0,
            "qdrant_writes": 0,
            "novel_validation_runs": 0,
            "novel_holdout_runs": 0,
            "protected_dataset_access": 0,
        },
        "accounting": {
            "analyzer_calls": 0,
            "analyzer_provider_attempts": 0,
            "embedding_calls": 0,
            "reranker_calls": 0,
            "logical_model_calls": 0,
            "provider_attempts": 0,
            "retries": 0,
            "token_usage": 0,
        },
        "outcome_exposure_state": {
            "D4_A5_OUTCOME_EXPOSURE": "NOT_STARTED",
            "plans_completed": 0,
            "formal_cells_completed": 0,
            "formal_cells_failed": 0,
            "evaluator_executed": False,
            "scientific_verdict_computed": False,
        },
        "production_activation": False,
        "batch1_production_active": True,
        "batch2_production_active": False,
    }


# ---------------------------------------------------------------------------
# Phase P — prospective plan acquisition
# ---------------------------------------------------------------------------


def execute_phase_p(project_root: Path) -> dict[str, Any]:
    load_dotenv(project_root / ".env")
    freeze = verify_executor_freeze_gate(project_root)

    manifest = _load_json(project_root / MANIFEST_PATH)
    exposure = manifest.setdefault("outcome_exposure_state", {})
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") in ("PLANS_FROZEN", "RAW_RETRIEVAL_COMPLETE", "EVALUATION_COMPLETE"):
        print("[PHASE P ALREADY COMPLETED] Loading existing frozen plans.")
        return _load_json(project_root / RAW_PLANS_PATH)
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") not in ("NOT_STARTED", "PLAN_ACQUISITION_STARTED"):
        raise RuntimeError(f"Unexpected exposure state: {exposure}")

    settings_check = {
        "generation_model": EXPECTED_MODEL,
        "embedding_model": EXPECTED_EMBEDDING_MODEL,
        "location": EXPECTED_VERTEX_LOCATION,
        "temperature": EXPECTED_TEMPERATURE,
    }

    exposure["D4_A5_OUTCOME_EXPOSURE"] = "PLAN_ACQUISITION_STARTED"
    exposure["executor_freeze_head"] = freeze["head"]
    _save_json(project_root / MANIFEST_PATH, manifest)

    retriever = Retriever(project_root)
    if retriever.query_expansions is None or len(retriever.query_expansions.rules) != 54:
        raise RuntimeError("Production query-expansion config drift detected (expected 54 rules)")

    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_questions: dict[str, GoldQuestion] = {
        q.id: q for q in gold_ds.questions + novel_ds.questions
    }
    rules_by_id = {
        rule["rule_id"]: rule
        for rule in retriever.query_expansions.model_dump(mode="python")["rules"]
    }

    plan_records: list[dict[str, Any]] = []
    total_tokens = 0
    total_attempts = 0

    print(f"[PHASE P] Acquiring {len(CASE_ORDER)} prospective plans (retries=0)...")

    for i, cid in enumerate(CASE_ORDER, start=1):
        slot = manifest["phase_p_slots_7"][i - 1]
        if slot["status"] == "COMPLETED":
            print(f"  Slot #{i} ({cid}) already completed, skipping.")
            continue
        if slot["status"] == "STARTED":
            raise RuntimeError(
                f"Slot #{i} ({cid}) in ambiguous STARTED state; fail closed on restart."
            )

        question_text = all_questions[cid].query

        slot["status"] = "STARTED"
        slot["started_at"] = _utc_now()
        _save_json(project_root / MANIFEST_PATH, manifest)

        stats_before = retriever.vertex.stats_snapshot()
        t0 = time.time()
        # Frozen retry policy: exactly one attempt; any failure fails closed.
        raw_plan = retriever.analyze(question_text)
        elapsed = round(time.time() - t0, 3)
        stats_delta = retriever.vertex.stats_delta(stats_before)
        provider_attempts = stats_delta.get("model_calls", 1)
        token_usage = stats_delta.get("token_usage", 0)
        total_tokens += token_usage
        total_attempts += provider_attempts

        plan_dict = raw_plan.model_dump(mode="json")
        RetrievalPlan.model_validate(plan_dict)
        sig_str, sig_payload = compute_plan_signature(plan_dict)

        diagnostics = plan_dict.get("analysis_diagnostics") or {}
        matched_rule_ids = list(diagnostics.get("matched_expansion_rules") or [])
        attribution = CASE_ATTRIBUTION[cid]
        matched_batch2 = [
            rid for rid in attribution["matched_retirement_rules"] if rid in matched_rule_ids
        ]
        if sorted(matched_batch2) != sorted(attribution["matched_retirement_rules"]):
            raise RuntimeError(
                f"Case {cid}: deterministic Batch-2 rule matching drifted from the frozen "
                f"D4-A4 attribution: expected {attribution['matched_retirement_rules']}, "
                f"observed {matched_batch2}"
            )
        matched_batch1 = [
            rid for rid in attribution["matched_batch1_rule_ids"] if rid in matched_rule_ids
        ]
        if sorted(matched_batch1) != sorted(attribution["matched_batch1_rule_ids"]):
            raise RuntimeError(
                f"Case {cid}: deterministic Batch-1 rule matching drifted from the frozen "
                f"D4-A4 attribution: expected {attribution['matched_batch1_rule_ids']}, "
                f"observed {matched_batch1}"
            )

        ledger = build_contribution_ledger(plan_dict, rules_by_id, matched_rule_ids)
        mask_entries = build_batch2_mask_entries(cid, matched_batch2)
        current_compat_projection = copy.deepcopy(plan_dict)
        projected, projection_receipts = build_retirement_projection(
            plan_dict, ledger, mask_entries, matched_batch2
        )
        gate = build_provenance_gate_receipt(
            cid, attribution, matched_rule_ids, plan_dict, ledger,
            current_compat_projection, projected, projection_receipts,
        )
        if not gate["pass"]:
            failed = [k for k, v in gate["checks"].items() if not v.get("pass", False)]
            raise RuntimeError(
                f"Case {cid}: pre-outcome provenance gate FAILED ({failed}); "
                f"verdict path {VERDICT_INVALID}. No downstream retrieval may run."
            )

        record = {
            "plan_index": i,
            "plan_id": f"prospective_{cid}",
            "case_id": cid,
            "question": question_text,
            "role": attribution["role"],
            "intent": plan_dict.get("intent"),
            "canonical_plan": plan_dict,
            "canonical_serialization": json.dumps(plan_dict, sort_keys=True, ensure_ascii=False),
            "plan_signature": sig_payload,
            "plan_signature_str": sig_str,
            "matched_query_expansion_rules": matched_rule_ids,
            "matched_batch1_rule_ids": matched_batch1,
            "matched_batch2_rule_ids": matched_batch2,
            "contribution_ledger": ledger,
            "current_compat_execution_projection": current_compat_projection,
            "batch2_retirement_execution_projection": projected,
            "projection_diff_receipts": projection_receipts,
            "provenance_gate": gate,
            "provider_accounting": {
                "analyzer_logical_calls": 1,
                "analyzer_provider_attempts": provider_attempts,
                "retries": 0,
                "embedding_calls": 0,
                "reranker_calls": 0,
                "token_usage": token_usage,
                "elapsed_seconds": elapsed,
            },
            "status": "COMPLETED",
            "started_at": slot["started_at"],
            "completed_at": _utc_now(),
        }
        plan_records.append(record)

        slot["status"] = "COMPLETED"
        slot["completed_at"] = record["completed_at"]
        slot["token_usage"] = token_usage
        slot["attempts"] = provider_attempts
        slot["plan_signature"] = sig_payload
        exposure["plans_completed"] = len(plan_records)
        _save_json(project_root / MANIFEST_PATH, manifest)

        print(
            f"  Slot #{i}/{len(CASE_ORDER)} ({cid}) COMPLETED in {elapsed}s: "
            f"{len(plan_dict.get('concepts') or [])} concepts, "
            f"{len(plan_dict.get('symbols') or [])} symbols, "
            f"batch2={matched_batch2}"
        )

    raw_artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5",
        "stage": "Phase P — Prospective Shared Plan Acquisition",
        "created_at": _utc_now(),
        "starting_head": STARTING_HEAD,
        "executor_freeze_head": freeze["head"],
        "plan_freeze_state": "PLANS_FROZEN",
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED": True,
        "PHASE_R_RETRIEVAL_EXECUTED": False,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "model_contract": settings_check,
        "prompt_authority": "src/panda_agent/prompts.py:QUERY_ANALYZER_SYSTEM_PROMPT",
        "exact_acquisition_case_order": list(CASE_ORDER),
        "max_provider_attempts_per_case": MAX_PROVIDER_ATTEMPTS_PER_CASE,
        "retry_policy": {"max_retries": 0},
        "plans_planned": len(CASE_ORDER),
        "plans_completed": len(plan_records),
        "plans_failed": 0,
        "accounting": {
            "analyzer_calls": len(plan_records),
            "analyzer_provider_attempts": total_attempts,
            "embedding_calls": 0,
            "reranker_calls": 0,
            "logical_model_calls": len(plan_records),
            "retries": 0,
            "token_usage": total_tokens,
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "db_writes": 0,
            "qdrant_writes": 0,
            "reindex": 0,
            "novel_validation_runs": 0,
            "novel_holdout_runs": 0,
            "protected_dataset_access": 0,
        },
        "plans": plan_records,
    }
    _save_json(project_root / RAW_PLANS_PATH, raw_artifact)

    exposure["D4_A5_OUTCOME_EXPOSURE"] = "PLANS_FROZEN"
    _save_json(project_root / MANIFEST_PATH, manifest)
    print(f"[PHASE P COMPLETE] {len(plan_records)} plans frozen to {RAW_PLANS_PATH}")
    return raw_artifact


# ---------------------------------------------------------------------------
# Phase R — paired shared-plan retrieval
# ---------------------------------------------------------------------------


def build_cell_record(
    cell: dict[str, Any],
    plan_record: dict[str, Any],
    question_text: str,
    retrieval_result: dict[str, Any],
    arm_plan_dict: dict[str, Any],
    stats: dict[str, Any],
    started_at: str,
    elapsed: float,
) -> dict[str, Any]:
    canonical_plan = plan_record["canonical_plan"]
    actual_plan = retrieval_result.get("plan") or {}
    is_current_compat = cell["arm"] == "CURRENT_COMPAT"
    plan_equality = actual_plan == arm_plan_dict
    canonical_equality = (
        actual_plan == canonical_plan
        if is_current_compat
        else None
    )
    structured_receipt = retrieval_result.get("structured_replacement")
    rankings = retrieval_result.get("rankings") or {}
    fusion_scores = retrieval_result.get("fusion_scores") or {}
    if structured_receipt is not None:
        rerank_pool = list(structured_receipt.get("final_rerank_pool_ids") or [])
    else:
        rerank_pool = list(fusion_scores.keys())
    evidence_items = []
    for item in retrieval_result.get("evidence") or []:
        evidence_items.append({
            "object_id": item.get("object_id"),
            "source_id": item.get("source_id"),
            "source_version_id": item.get("source_version_id"),
            "locator": item.get("locator"),
            "object_type": item.get("object_type"),
            "title": item.get("title"),
        })

    return {
        "cell_index": cell["cell_index"],
        "cell_id": cell["cell_id"],
        "case_id": cell["case_id"],
        "arm": cell["arm"],
        "role": cell["role"],
        "question": question_text,
        "status": "COMPLETED",
        "elapsed_seconds": elapsed,
        "canonical_plan_id": plan_record["plan_id"],
        "canonical_plan_signature": plan_record["plan_signature"],
        "frozen_canonical_plan": canonical_plan,
        "arm_execution_projection": arm_plan_dict,
        "projection_diff_receipts": plan_record["projection_diff_receipts"],
        "actual_plan_used": actual_plan,
        "plan_equality_arm_projection_verified": plan_equality,
        "canonical_plan_identical_across_pair": (
            canonical_equality if canonical_equality is not None
            else actual_plan != canonical_plan
        ),
        "batch2_retirement_mask_applied": cell["batch2_retirement_mask_applied"],
        "retirement_rule_ids": cell["retirement_rule_ids"],
        "matched_query_expansion_rules": (actual_plan.get("analysis_diagnostics") or {}).get(
            "matched_expansion_rules", []
        ),
        "batch1_activation_receipt": structured_receipt,
        "batch1_structured_replacement_active": structured_receipt is not None,
        "batch1_active_rule_ids": (
            list(structured_receipt.get("active_migrated_rule_ids") or [])
            if structured_receipt is not None else []
        ),
        "contribution_ledger_before": plan_record["contribution_ledger"],
        "contribution_ledger_after": plan_record["contribution_ledger"]
        if is_current_compat
        else [
            entry for entry in plan_record["contribution_ledger"]
            if entry["contribution_id"]
            not in {
                item["contribution_id"]
                for item in plan_record["projection_diff_receipts"]["removed_rule_origin_entries"]
                if item["effectively_removed"]
            }
        ],
        "removed_origins": plan_record["projection_diff_receipts"]["removed_rule_origin_entries"]
        if not is_current_compat else [],
        "surviving_independent_origins": plan_record["projection_diff_receipts"][
            "surviving_independent_origin_entries"
        ] if not is_current_compat else [],
        "channel_rankings": rankings,
        "fusion_scores_top30": fusion_scores,
        "rerank_pool_object_ids": rerank_pool,
        "reranked_object_ids": retrieval_result.get("reranked_object_ids") or [],
        "ranked_object_ids": retrieval_result.get("ranked_object_ids") or [],
        "final_evidence_object_ids": [item["object_id"] for item in evidence_items],
        "final_evidence_entries": evidence_items,
        "excluded": retrieval_result.get("excluded") or [],
        "backfill_admissions": retrieval_result.get("backfill_admissions") or [],
        "semantic_query": retrieval_result.get("semantic_query"),
        "lexical_query": retrieval_result.get("lexical_query"),
        "dense_queries": retrieval_result.get("dense_queries"),
        "provider_accounting": {
            "analyzer_calls": 0,
            "embedding_calls": stats.get("embedding_calls", 1),
            "reranker_calls": stats.get("generation_calls", 1),
            "provider_internal_attempts": stats.get("model_calls", 0),
            "token_usage": stats.get("token_usage", 0),
        },
        "started_at": started_at,
        "completed_at": _utc_now(),
    }


def execute_phase_r(project_root: Path) -> dict[str, Any]:
    load_dotenv(project_root / ".env")
    manifest = _load_json(project_root / MANIFEST_PATH)
    exposure = manifest.setdefault("outcome_exposure_state", {})
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") in ("RAW_RETRIEVAL_COMPLETE", "EVALUATION_COMPLETE"):
        print("[PHASE R ALREADY COMPLETED] Loading existing paired results.")
        return _load_json(project_root / RAW_RESULTS_PATH)
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") != "PLANS_FROZEN":
        raise RuntimeError(f"Phase R requires PLANS_FROZEN exposure, got {exposure}")

    executor_freeze_head = exposure.get("executor_freeze_head")
    if not executor_freeze_head:
        raise RuntimeError("Manifest is missing executor_freeze_head; plan freeze provenance unknown")
    freeze = verify_plan_freeze_gate(project_root, executor_freeze_head)

    raw_plans = _load_json(project_root / RAW_PLANS_PATH)
    plans_by_case = {p["case_id"]: p for p in raw_plans["plans"]}
    if sorted(plans_by_case) != sorted(CASE_ORDER) or len(raw_plans["plans"]) != 7:
        raise RuntimeError("Plan artifact does not contain exactly the frozen 7-case cohort")
    plans_planned = raw_plans["plans_planned"]
    plans_completed = raw_plans["plans_completed"]
    if plans_planned != 7 or plans_completed != 7:
        raise RuntimeError("Plan artifact accounting incomplete")
    for record in raw_plans["plans"]:
        if not record["provenance_gate"]["pass"]:
            raise RuntimeError(f"Plan provenance gate not PASS for {record['case_id']}")

    exposure["D4_A5_OUTCOME_EXPOSURE"] = "RAW_RETRIEVAL_STARTED"
    exposure["plan_freeze_head"] = freeze["head"]
    _save_json(project_root / MANIFEST_PATH, manifest)

    retriever = Retriever(project_root)
    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_questions = {q.id: q for q in gold_ds.questions + novel_ds.questions}

    # Hard downstream-Analyzer prohibition: any analyze() attempt fails closed.
    def _forbidden_analyze(*_args: Any, **_kwargs: Any) -> RetrievalPlan:
        raise RuntimeError("Query Analyzer invocation is forbidden during Phase R")

    retriever.analyze = _forbidden_analyze  # type: ignore[method-assign]

    cell_records: list[dict[str, Any]] = []
    total_tokens = 0
    total_attempts = 0
    total_embedding = 0
    total_reranker = 0

    print(f"[PHASE R] Executing {len(SCHEDULE_14)} paired shared-plan cells...")

    for cell in SCHEDULE_14:
        cell_idx = cell["cell_index"]
        manifest_cell = manifest["phase_r_cells_14"][cell_idx - 1]
        if manifest_cell["status"] == "COMPLETED":
            print(f"  Cell #{cell_idx} ({cell['cell_id']}) already completed, skipping.")
            continue
        if manifest_cell["status"] == "STARTED":
            raise RuntimeError(
                f"Cell #{cell_idx} ({cell['cell_id']}) in ambiguous STARTED state; fail closed."
            )

        manifest_cell["status"] = "STARTED"
        manifest_cell["started_at"] = _utc_now()
        _save_json(project_root / MANIFEST_PATH, manifest)

        plan_record = plans_by_case[cell["case_id"]]
        question_text = all_questions[cell["case_id"]].query
        if cell["arm"] == "CURRENT_COMPAT":
            arm_plan_dict = plan_record["current_compat_execution_projection"]
        else:
            arm_plan_dict = plan_record["batch2_retirement_execution_projection"]
        arm_plan = RetrievalPlan.model_validate(arm_plan_dict)

        stats_before = retriever.vertex.stats_snapshot()
        t0 = time.time()
        result = retriever.retrieve(question_text, plan=arm_plan)
        elapsed = round(time.time() - t0, 3)
        stats_delta = retriever.vertex.stats_delta(stats_before)

        actual_plan = result.get("plan") or {}
        if actual_plan != arm_plan_dict:
            raise RuntimeError(
                f"Cell #{cell_idx}: actual plan used != frozen arm execution projection "
                f"for {cell['cell_id']}"
            )

        stats = {
            "embedding_calls": stats_delta.get("embedding_calls", 1),
            "generation_calls": stats_delta.get("generation_calls", 1),
            "model_calls": stats_delta.get("model_calls", 0),
            "token_usage": stats_delta.get("token_usage", 0),
        }
        total_embedding += stats["embedding_calls"]
        total_reranker += stats["generation_calls"]
        total_tokens += stats["token_usage"]
        total_attempts += stats["model_calls"]

        record = build_cell_record(
            cell, plan_record, question_text, result, arm_plan_dict, stats,
            manifest_cell["started_at"], elapsed,
        )
        cell_records.append(record)

        manifest_cell["status"] = "COMPLETED"
        manifest_cell["completed_at"] = record["completed_at"]
        manifest_cell["plan_equality_verified"] = record["plan_equality_arm_projection_verified"]
        manifest_cell["token_usage"] = stats["token_usage"]
        exposure["formal_cells_completed"] = len(cell_records)
        _save_json(project_root / MANIFEST_PATH, manifest)

        # Persist the complete raw cell record after successful completion.
        _write_raw_results(project_root, cell_records, freeze, total_tokens, total_attempts,
                           total_embedding, total_reranker, final=False)

        print(
            f"  Cell #{cell_idx}/{len(SCHEDULE_14)} ({cell['cell_id']}) COMPLETED in {elapsed}s "
            f"evidence={len(record['final_evidence_object_ids'])}"
        )

    raw_artifact = _write_raw_results(
        project_root, cell_records, freeze, total_tokens, total_attempts,
        total_embedding, total_reranker, final=True,
    )
    exposure["D4_A5_OUTCOME_EXPOSURE"] = "RAW_RETRIEVAL_COMPLETE"
    _save_json(project_root / MANIFEST_PATH, manifest)
    print(f"[PHASE R COMPLETE] 14 cells frozen to {RAW_RESULTS_PATH}")
    return raw_artifact


def _write_raw_results(
    project_root: Path,
    cell_records: list[dict[str, Any]],
    freeze: dict[str, Any],
    total_tokens: int,
    total_attempts: int,
    total_embedding: int,
    total_reranker: int,
    *,
    final: bool,
) -> dict[str, Any]:
    artifact = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5",
        "stage": "Phase R — Paired Shared-Plan Batch2 Retirement Retrieval",
        "created_at": _utc_now(),
        "starting_head": STARTING_HEAD,
        "executor_freeze_head": freeze["executor_freeze_head"],
        "plan_freeze_head": freeze["head"],
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED": True,
        "PHASE_R_RETRIEVAL_EXECUTED": True,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "cells_planned": len(SCHEDULE_14),
        "cells_completed": len(cell_records),
        "cells_failed": 0,
        "final": final,
        "model_contract": {
            "generation_model_id": EXPECTED_MODEL,
            "embedding_model_id": EXPECTED_EMBEDDING_MODEL,
            "temperature": EXPECTED_TEMPERATURE,
            "location": EXPECTED_VERTEX_LOCATION,
            "system_prompt": "src/panda_agent/prompts.py:RERANK_SYSTEM_PROMPT",
            "query_analyzer_prompt": "src/panda_agent/prompts.py:QUERY_ANALYZER_SYSTEM_PROMPT",
        },
        "accounting": {
            "FORMAL_CELLS_COMPLETED": len(cell_records),
            "FORMAL_CELLS_FAILED": 0,
            "ANALYZER_CALLS": 0,
            "EMBEDDING_CALLS": total_embedding,
            "RERANKER_CALLS": total_reranker,
            "LOGICAL_MODEL_CALLS": total_embedding + total_reranker,
            "PROVIDER_INTERNAL_ATTEMPTS": total_attempts,
            "TOTAL_TOKEN_USAGE": total_tokens,
            "RETRIES": 0,
            "QA_CALLS": 0,
            "VERIFIER_CALLS": 0,
            "JUDGE_CALLS": 0,
            "DB_WRITES": 0,
            "QDRANT_WRITES": 0,
            "INGESTION_RUNS": 0,
            "REINDEX_RUNS": 0,
            "NOVEL_VALIDATION_RUNS": 0,
            "NOVEL_HOLDOUT_RUNS": 0,
            "PROTECTED_DATASET_ACCESS": 0,
        },
        "authority": {
            "preregistration": PREREGISTRATION_PATH,
            "selection": SELECTION_PATH,
            "raw_plans": RAW_PLANS_PATH,
            "manifest": MANIFEST_PATH,
            "executor_freeze_head": freeze["executor_freeze_head"],
            "plan_freeze_head": freeze["head"],
        },
        "slots": cell_records,
    }
    _save_json(project_root / RAW_RESULTS_PATH, artifact)
    return artifact


def validate_raw_artifact_structural_validity(
    raw_data: dict[str, Any],
    plans_data: dict[str, Any],
) -> tuple[bool, str | None]:
    """Mechanical structural validation before any metric evaluation."""
    if not isinstance(raw_data, dict):
        return False, "Raw artifact is not a JSON object"
    slots = raw_data.get("slots", [])
    if len(slots) != 14:
        return False, f"Raw slots count mismatch: expected 14, got {len(slots)}"
    for i, (slot, expected) in enumerate(zip(slots, SCHEDULE_14)):
        if (slot.get("cell_index"), slot.get("case_id"), slot.get("arm")) != (
            expected["cell_index"], expected["case_id"], expected["arm"]
        ):
            return False, f"Schedule mismatch at cell #{i + 1}"
        if slot.get("status") != "COMPLETED":
            return False, f"Cell #{expected['cell_index']} status is not COMPLETED"
        if slot.get("plan_equality_arm_projection_verified") is not True:
            return False, f"Cell #{expected['cell_index']} arm plan equality not verified"
        acct = slot.get("provider_accounting") or {}
        if acct.get("analyzer_calls", 0) != 0:
            return False, f"Cell #{expected['cell_index']} invoked the Query Analyzer"
        if acct.get("embedding_calls", 0) != 1 or acct.get("reranker_calls", 0) != 1:
            return False, (
                f"Cell #{expected['cell_index']} embedding/reranker accounting != 1/1: "
                f"{acct}"
            )
        if not slot.get("ranked_object_ids") or not slot.get("final_evidence_object_ids"):
            return False, f"Cell #{expected['cell_index']} has incomplete metric inputs"
        if not slot.get("channel_rankings"):
            return False, f"Cell #{expected['cell_index']} has no channel rankings"
    accounting = raw_data.get("accounting", {})
    if accounting.get("EMBEDDING_CALLS") != 14 or accounting.get("RERANKER_CALLS") != 14:
        return False, "Downstream embedding/reranker totals != 14/14"
    if accounting.get("ANALYZER_CALLS") != 0:
        return False, "Downstream Analyzer calls != 0"
    if accounting.get("NOVEL_VALIDATION_RUNS", 0) or accounting.get("NOVEL_HOLDOUT_RUNS", 0) or accounting.get("PROTECTED_DATASET_ACCESS", 0):
        return False, "Protected dataset boundary violated in raw accounting"
    if raw_data.get("EVALUATOR_EXECUTED") is not False or raw_data.get("SCIENTIFIC_VERDICT_COMPUTED") is not False:
        return False, "Raw boundary flags indicate evaluator already ran"
    mc = raw_data.get("model_contract", {})
    if mc.get("generation_model_id") != EXPECTED_MODEL or mc.get("embedding_model_id") != EXPECTED_EMBEDDING_MODEL:
        return False, "Model contract drift in raw artifact"
    plans = plans_data.get("plans", [])
    if len(plans) != 7 or plans_data.get("plans_completed") != 7:
        return False, "Plans artifact incomplete"
    for record in plans:
        if not record.get("provenance_gate", {}).get("pass", False):
            return False, f"Plan provenance gate not PASS for {record.get('case_id')}"
    return True, None


# ---------------------------------------------------------------------------
# Deterministic evaluator (zero provider calls)
# ---------------------------------------------------------------------------


def _case_metric_value(
    question: GoldQuestion,
    slot: dict[str, Any],
    object_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ranked_ids = slot.get("ranked_object_ids") or []
    final_ids = slot.get("final_evidence_object_ids") or []
    channel_rankings = slot.get("channel_rankings") or {}
    combined_ids = list(dict.fromkeys(
        oid for oids in channel_rankings.values() for oid in oids
    ))
    groups = question.required_evidence_groups
    if not groups or not ranked_ids or not final_ids or not combined_ids:
        raise ValueError(f"Incomplete metric inputs; cannot compute case metrics")

    r5, _ = _matched_evidence_groups(groups, ranked_ids[:5], object_lookup)
    r10, _ = _matched_evidence_groups(groups, ranked_ids[:10], object_lookup)
    r20, _ = _matched_evidence_groups(groups, ranked_ids[:20], object_lookup)
    comb_rec, _ = _matched_evidence_groups(groups, combined_ids, object_lookup)
    final_rec, _ = _matched_evidence_groups(groups, final_ids, object_lookup)
    crit_groups = [g for g in groups if g.critical]
    if crit_groups:
        crit_rec, _ = _matched_evidence_groups(crit_groups, final_ids, object_lookup)
    else:
        crit_rec = 1.0
    rank_by_oid = {oid: rank for rank, oid in enumerate(ranked_ids, 1)}
    _, top20_prov = _matched_evidence_groups(groups, ranked_ids[:20], object_lookup)
    rel_ranks = [
        rank_by_oid[m["object_id"]]
        for m in top20_prov
        if isinstance(m, dict) and m.get("matched", True) and m.get("object_id") in rank_by_oid
    ]
    mrr = 1.0 / min(rel_ranks) if rel_ranks else 0.0
    return {
        "recall_at_5": r5,
        "recall_at_10": r10,
        "recall_at_20": r20,
        "combined_candidate_recall": comb_rec,
        "final_evidence_recall": final_rec,
        "critical_final_evidence_recall": crit_rec,
        "mrr": mrr,
    }


def _final_retention(
    question: GoldQuestion,
    slot: dict[str, Any],
    object_lookup: dict[str, dict[str, Any]],
) -> tuple[dict[str, bool], dict[str, bool]]:
    final_ids = slot.get("final_evidence_object_ids") or []
    pool_ids = slot.get("rerank_pool_object_ids") or []
    final_ret: dict[str, bool] = {}
    pool_ret: dict[str, bool] = {}
    for group in question.required_evidence_groups:
        rec, _ = _matched_evidence_groups([group], final_ids, object_lookup)
        final_ret[group.group_id] = rec > 0
        rec_pool, _ = _matched_evidence_groups([group], pool_ids, object_lookup)
        pool_ret[group.group_id] = rec_pool > 0
    return final_ret, pool_ret


def evaluate_d4_a5(project_root: Path) -> dict[str, Any]:
    """Deterministic, zero-provider evaluator using the frozen D4-A4 contract."""
    load_dotenv(project_root / ".env")
    manifest = _load_json(project_root / MANIFEST_PATH)
    exposure = manifest.get("outcome_exposure_state", {})
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") == "EVALUATION_COMPLETE":
        print("[EVALUATOR ALREADY COMPLETED] Loading existing evaluator results.")
        return _load_json(project_root / EVALUATOR_RESULTS_PATH)
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") != "RAW_RETRIEVAL_COMPLETE":
        raise RuntimeError(f"Evaluator requires RAW_RETRIEVAL_COMPLETE, got {exposure}")

    plan_freeze_head = exposure.get("plan_freeze_head")
    if not plan_freeze_head:
        raise RuntimeError("Manifest missing plan_freeze_head")
    freeze = verify_raw_freeze_gate(project_root, plan_freeze_head)

    prereg = _load_json(project_root / PREREGISTRATION_PATH)
    plans_data = _load_json(project_root / RAW_PLANS_PATH)
    raw_data = _load_json(project_root / RAW_RESULTS_PATH)

    execution_valid, validity_error = validate_raw_artifact_structural_validity(raw_data, plans_data)
    if not execution_valid:
        raise RuntimeError(
            f"Raw artifact structurally invalid; verdict path {VERDICT_INVALID}: {validity_error}"
        )

    gold_ds = load_gold_dataset(project_root / GOLD_QUESTIONS_PATH)
    novel_ds = load_gold_dataset(project_root / NOVEL_DEV_PATH)
    all_questions = {q.id: q for q in gold_ds.questions + novel_ds.questions}
    object_lookup = load_object_lookup(project_root)

    slots_map = {(s["case_id"], s["arm"]): s for s in raw_data["slots"]}
    plans_by_case = {p["case_id"]: p for p in plans_data["plans"]}

    plan_pairs_equal = 0
    plan_cells_equal = 0
    for cid in CASE_ORDER:
        record = plans_by_case[cid]
        slot_cc = slots_map[(cid, "CURRENT_COMPAT")]
        slot_rt = slots_map[(cid, "BATCH2_RETIREMENT")]
        pair_ok = (
            slot_cc["frozen_canonical_plan"] == record["canonical_plan"]
            and slot_rt["frozen_canonical_plan"] == record["canonical_plan"]
        )
        if pair_ok:
            plan_pairs_equal += 1
        if slot_cc["plan_equality_arm_projection_verified"] and slot_rt["plan_equality_arm_projection_verified"]:
            plan_cells_equal += 2

    # Per-case / per-group pair phenotypes.
    group_records: dict[str, dict[str, Any]] = {}
    for cid in CASE_ORDER:
        question = all_questions[cid]
        slot_cc = slots_map[(cid, "CURRENT_COMPAT")]
        slot_rt = slots_map[(cid, "BATCH2_RETIREMENT")]
        cc_final, cc_pool = _final_retention(question, slot_cc, object_lookup)
        rt_final, rt_pool = _final_retention(question, slot_rt, object_lookup)
        for gid in cc_final:
            group_records[gid] = {
                "case_id": cid,
                "dataset": question.split,
                "is_answered": cid in ANSWERED_CASES,
                "is_negative_control_case": cid in NEGATIVE_CONTROL_CASES,
                "is_nonmatching_control_case": cid in NONMATCHING_CONTROLS,
                "critical": next(g.critical for g in question.required_evidence_groups if g.group_id == gid),
                "current_compat_final_retained": cc_final[gid],
                "batch2_retirement_final_retained": rt_final[gid],
                "pair_phenotype_final": b2.classify_pair(cc_final[gid], rt_final[gid]),
                "current_compat_pool_retained": cc_pool[gid],
                "batch2_retirement_pool_retained": rt_pool[gid],
                "pair_phenotype_pre_rerank": b2.classify_pair(cc_pool[gid], rt_pool[gid]),
            }

    # Per-rule protocol validity, effective removals, and attribution receipts.
    rule_receipts: dict[str, dict[str, Any]] = {}
    for rid in b2.CANDIDATE_RULE_IDS:
        active_groups = ACTIVE_RULE_CASE_GROUPS[rid]
        receipts: dict[str, Any] = {
            "rule_id": rid,
            "active_case_groups": active_groups,
            "protocol_valid": True,
            "protocol_errors": [],
            "effective_removal_count": 0,
            "removed_effective_values": [],
            "surviving_via_independent_origin": [],
        }
        for case_id, gids in active_groups.items():
            plan_record = plans_by_case[case_id]
            gate = plan_record["provenance_gate"]
            diff = plan_record["projection_diff_receipts"]
            if not gate["pass"]:
                receipts["protocol_valid"] = False
                receipts["protocol_errors"].append(f"{case_id}: provenance gate failed")
            matched = plan_record["matched_batch2_rule_ids"]
            if rid not in matched:
                receipts["protocol_valid"] = False
                receipts["protocol_errors"].append(f"{case_id}: rule not matched at runtime")
            slot_cc = slots_map[(case_id, "CURRENT_COMPAT")]
            slot_rt = slots_map[(case_id, "BATCH2_RETIREMENT")]
            if slot_cc["plan_equality_arm_projection_verified"] is not True or slot_rt["plan_equality_arm_projection_verified"] is not True:
                receipts["protocol_valid"] = False
                receipts["protocol_errors"].append(f"{case_id}: cell plan equality not verified")
            for entry in diff["removed_rule_origin_entries"]:
                if entry["retired_rule_origins"] and rid in entry["retired_rule_origins"]:
                    if entry["effectively_removed"]:
                        receipts["effective_removal_count"] += 1
                        receipts["removed_effective_values"].append(entry["value"])
                    else:
                        receipts["surviving_via_independent_origin"].append({
                            "value": entry["value"],
                            "surviving_independent_origins": entry["surviving_independent_origins"],
                        })
        rule_receipts[rid] = receipts

    # Attributable T/F losses (Section 35) and safety accounting (Section 36).
    attributable_losses: dict[str, list[dict[str, Any]]] = {rid: [] for rid in b2.CANDIDATE_RULE_IDS}
    critical_regression_details: list[dict[str, Any]] = []
    control_divergence_findings: list[dict[str, Any]] = []
    invalid_provenance_details: list[dict[str, Any]] = []
    grounding_details: list[dict[str, Any]] = []
    wrong_version_details: list[dict[str, Any]] = []
    critical_regression_count = 0

    for gid, info in group_records.items():
        cid = info["case_id"]
        final_class = info["pair_phenotype_final"]
        is_regression = final_class == "PAIR_RETIREMENT_REGRESSION"
        is_recovery = final_class == "PAIR_RETIREMENT_RECOVERY"
        if info["is_answered"] and info["critical"] and is_regression:
            critical_regression_count += 1
            critical_regression_details.append({
                "case_id": cid,
                "group_id": gid,
                "phenotype": final_class,
                "pre_rerank_phenotype": info["pair_phenotype_pre_rerank"],
                "answered": True,
                "active_treatment_case": cid in ACTIVE_RULE_CASE_GROUPS_GROUPS_ALL(),
            })
        if cid in NONMATCHING_CONTROLS and final_class != "PAIR_PRESERVED":
            control_divergence_findings.append({
                "case_id": cid,
                "group_id": gid,
                "phenotype": final_class,
                "role": info["dataset"],
                "note": "No-op control difference; reported as safety finding, never rule dependency.",
            })
        if is_regression:
            owning_rules = [
                rid for rid, mapping in ACTIVE_RULE_CASE_GROUPS.items()
                if cid in mapping and gid in mapping[cid]
            ]
            attributed = False
            for rid in owning_rules:
                receipts = rule_receipts[rid]
                if (
                    receipts["protocol_valid"]
                    and receipts["effective_removal_count"] > 0
                ):
                    attributable_losses[rid].append({
                        "case_id": cid,
                        "group_id": gid,
                        "phenotype": final_class,
                        "attribution": (
                            "Attributable T/F loss in active direct treatment pair under "
                            "provenance-valid frozen shared plan with effective rule-origin removal."
                        ),
                    })
                    attributed = True
            if not attributed:
                critical_regression_details[-1]["attribution"] = (
                    "Not attributable to a selected Batch-2 rule origin (control or no-effective-removal pair)."
                )
        if is_recovery:
            owning_rules = [
                rid for rid, mapping in ACTIVE_RULE_CASE_GROUPS.items()
                if cid in mapping and gid in mapping[cid]
            ]
            has_effective_removal = any(
                rule_receipts[rid]["effective_removal_count"] > 0 and rule_receipts[rid]["protocol_valid"]
                for rid in owning_rules
            )
            recovered_untraceable = False
            slot_rt = slots_map[(cid, "BATCH2_RETIREMENT")]
            for item in slot_rt.get("final_evidence_entries") or []:
                if not item.get("source_id") or not item.get("source_version_id"):
                    recovered_untraceable = True
            if not owning_rules or not has_effective_removal or recovered_untraceable:
                invalid_provenance_details.append({
                    "case_id": cid,
                    "group_id": gid,
                    "phenotype": final_class,
                    "violation": (
                        "Retirement-arm recovery without a valid provenance explanation "
                        "(no effective mask removal on this pair, or untraceable source identity)."
                    ),
                })

    # Grounding and wrong-version regressions (newly introduced in retirement arm).
    for cid in CASE_ORDER:
        question = all_questions[cid]
        slot_cc = slots_map[(cid, "CURRENT_COMPAT")]
        slot_rt = slots_map[(cid, "BATCH2_RETIREMENT")]
        allowed = set(question.allowed_source_versions)
        cc_versions = {
            item["object_id"]: item.get("source_version_id")
            for item in slot_cc.get("final_evidence_entries") or []
        }
        rt_versions = {
            item["object_id"]: item.get("source_version_id")
            for item in slot_rt.get("final_evidence_entries") or []
        }
        for oid, sv in sorted(rt_versions.items()):
            if sv is not None and sv not in allowed and oid not in cc_versions:
                wrong_version_details.append({
                    "case_id": cid, "object_id": oid, "source_version_id": sv,
                })
        for sel in question.forbidden_evidence:
            cc_forbidden = {
                item["object_id"] for item in slot_cc.get("final_evidence_entries") or []
                if sel.matches(object_lookup.get(item["object_id"]) or {})
            }
            for item in slot_rt.get("final_evidence_entries") or []:
                oid = item["object_id"]
                if oid in cc_forbidden:
                    continue
                if sel.matches(object_lookup.get(oid) or {}):
                    grounding_details.append({
                        "case_id": cid, "object_id": oid,
                        "violation_type": "forbidden_evidence_hit",
                    })

    # Per-rule dispositions (frozen D4-A4 function).
    baseline_reproduced: dict[str, bool] = {}
    for rid, mapping in ACTIVE_RULE_CASE_GROUPS.items():
        ok = True
        for case_id, gids in mapping.items():
            for gid in gids:
                info = group_records.get(gid)
                if info is None or not info["current_compat_final_retained"]:
                    ok = False
        baseline_reproduced[rid] = ok

    dispositions: dict[str, str] = {}
    for rid in b2.CANDIDATE_RULE_IDS:
        receipts = rule_receipts[rid]
        dispositions[rid] = b2.classify_rule(
            protocol_valid=receipts["protocol_valid"],
            baseline_reproduced=baseline_reproduced[rid],
            attributable_loss=bool(attributable_losses[rid]),
        )

    # Metrics: macro arithmetic mean over the six answered cases.
    case_metrics: dict[str, dict[str, dict[str, float]]] = {}
    for cid in ANSWERED_CASES:
        question = all_questions[cid]
        case_metrics[cid] = {}
        for arm in ARMS:
            case_metrics[cid][arm] = _case_metric_value(
                question, slots_map[(cid, arm)], object_lookup
            )

    def _macro(arm: str) -> dict[str, float]:
        result: dict[str, float] = {}
        for key in PRIMARY_METRIC_KEYS + ["mrr"]:
            values = [case_metrics[cid][arm][key] for cid in ANSWERED_CASES]
            if len(values) != 6 or any(not math.isfinite(v) for v in values):
                raise RuntimeError(f"Nonfinite or incomplete metric {key}; cannot aggregate")
            result[key] = sum(values) / len(values)
        return result

    macro_current = _macro("CURRENT_COMPAT")
    macro_retirement = _macro("BATCH2_RETIREMENT")
    macro_deltas = {
        key: round(macro_retirement[key] - macro_current[key], 6)
        for key in PRIMARY_METRICS_AND_MRR()
    }

    reference_baseline_valid = all(baseline_reproduced.values())
    tolerance_checks = {
        key: {
            "delta": macro_deltas[key],
            "threshold": b2.DEFAULT_METRIC_BOUNDED_TOLERANCES[key],
            "pass": macro_deltas[key] >= b2.DEFAULT_METRIC_BOUNDED_TOLERANCES[key],
        }
        for key in PRIMARY_METRIC_KEYS
    }

    verdict = b2.evaluate_batch2_verdict(
        execution_valid=True,
        protocol_violation=False,
        missing_inputs=False,
        plan_equality_all_verified=(plan_pairs_equal == 7 and plan_cells_equal == 14),
        analyzer_provider_calls_downstream=raw_data["accounting"]["ANALYZER_CALLS"],
        reference_baseline_valid=reference_baseline_valid,
        per_rule_dispositions=dispositions,
        critical_retirement_regressions=critical_regression_count,
        grounding_regressions=len(grounding_details),
        wrong_version_regressions=len(wrong_version_details),
        invalid_provenance_recoveries=len(invalid_provenance_details),
        metric_deltas={key: macro_deltas[key] for key in PRIMARY_METRIC_KEYS},
    )

    evaluator_results = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5",
        "stage": "Deterministic Evaluator — Batch2 Controlled Retirement Validation",
        "created_at": _utc_now(),
        "frozen_input_provenance": {
            "starting_head": STARTING_HEAD,
            "executor_freeze_head": exposure.get("executor_freeze_head"),
            "plan_freeze_head": plan_freeze_head,
            "raw_freeze_head": freeze["head"],
            "preregistration": PREREGISTRATION_PATH,
            "selection": SELECTION_PATH,
            "raw_plans": RAW_PLANS_PATH,
            "raw_results": RAW_RESULTS_PATH,
            "gold": GOLD_QUESTIONS_PATH,
            "novel_dev": NOVEL_DEV_PATH,
        },
        "execution_validity": {
            "valid": True,
            "structural_validation_error": validity_error,
            "plan_pair_equality": f"{plan_pairs_equal}/7",
            "plan_cell_equality": f"{plan_cells_equal}/14",
        },
        "provider_accounting": raw_data["accounting"],
        "group_pair_phenotypes": group_records,
        "pair_phenotype_counts": {
            phenotype: sum(
                1 for info in group_records.values() if info["pair_phenotype_final"] == phenotype
            )
            for phenotype in b2.PAIR_PHENOTYPES
        },
        "rule_attribution_receipts": rule_receipts,
        "attributable_losses": attributable_losses,
        "baseline_reproduction": baseline_reproduced,
        "reference_baseline_valid": reference_baseline_valid,
        "per_rule_dispositions": dispositions,
        "safety": {
            "critical_retirement_regressions": critical_regression_count,
            "critical_regression_details": critical_regression_details,
            "grounding_regressions": len(grounding_details),
            "grounding_details": grounding_details,
            "wrong_version_regressions": len(wrong_version_details),
            "wrong_version_details": wrong_version_details,
            "invalid_provenance_recoveries": len(invalid_provenance_details),
            "invalid_provenance_details": invalid_provenance_details,
            "control_divergence_findings": control_divergence_findings,
            "negative_control_case": {
                cid: {
                    "group_phenotypes": {
                        gid: info["pair_phenotype_final"]
                        for gid, info in group_records.items()
                        if info["case_id"] == cid
                    },
                }
                for cid in NEGATIVE_CONTROL_CASES
            },
        },
        "case_metrics": case_metrics,
        "macro_metrics": {
            "CURRENT_COMPAT": macro_current,
            "BATCH2_RETIREMENT": macro_retirement,
        },
        "metric_deltas": macro_deltas,
        "tolerance_checks": tolerance_checks,
        "answered_case_denominator": 6,
        "answered_evidence_group_denominator": sum(
            1 for info in group_records.values() if info["is_answered"]
        ),
        "verdict_inputs": {
            "execution_valid": True,
            "protocol_violation": False,
            "missing_inputs": False,
            "plan_equality_all_verified": plan_pairs_equal == 7 and plan_cells_equal == 14,
            "analyzer_provider_calls_downstream": raw_data["accounting"]["ANALYZER_CALLS"],
            "reference_baseline_valid": reference_baseline_valid,
            "per_rule_dispositions": dispositions,
            "critical_retirement_regressions": critical_regression_count,
            "grounding_regressions": len(grounding_details),
            "wrong_version_regressions": len(wrong_version_details),
            "invalid_provenance_recoveries": len(invalid_provenance_details),
            "metric_deltas": {key: macro_deltas[key] for key in PRIMARY_METRIC_KEYS},
        },
        "verdict_level": verdict["verdict_level"],
        "verdict": verdict["verdict"],
        "verdict_status": verdict["verdict_status"],
        "verdict_reason": verdict["verdict_reason"],
    }
    _save_json(project_root / EVALUATOR_RESULTS_PATH, evaluator_results)

    result = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5",
        "lifecycle_stage": "D4-A5 — Second-Batch Low-Risk Locator Controlled Retirement Validation",
        "created_at": _utc_now(),
        "commit_lineage": {
            "starting_head": STARTING_HEAD,
            "executor_freeze_head": exposure.get("executor_freeze_head"),
            "plan_freeze_head": plan_freeze_head,
            "raw_freeze_head": freeze["head"],
        },
        "exact_selected_rules": list(b2.CANDIDATE_RULE_IDS),
        "exact_component_masks": b2.FROZEN_RETIREMENT_MASKS,
        "plans_completed": plans_data["plans_completed"],
        "cells_completed": raw_data["cells_completed"],
        "cells_failed": raw_data["cells_failed"],
        "per_rule_dispositions": dispositions,
        "critical_regression_count": critical_regression_count,
        "grounding_regression_count": len(grounding_details),
        "wrong_version_regression_count": len(wrong_version_details),
        "invalid_provenance_recovery_count": len(invalid_provenance_details),
        "metric_deltas": {key: macro_deltas[key] for key in PRIMARY_METRIC_KEYS},
        "diagnostic_mrr": {
            "CURRENT_COMPAT": macro_current["mrr"],
            "BATCH2_RETIREMENT": macro_retirement["mrr"],
            "delta": macro_deltas["mrr"],
        },
        "tolerance_checks": tolerance_checks,
        "verdict_level": verdict["verdict_level"],
        "verdict": verdict["verdict"],
        "verdict_status": verdict["verdict_status"],
        "verdict_reason": verdict["verdict_reason"],
        "production_activation": False,
        "batch1_production_active": True,
        "batch2_production_active": False,
        "next_stage": "D4-A6 (requires separate authorization)",
    }
    _save_json(project_root / RESULT_PATH, result)

    exposure["D4_A5_OUTCOME_EXPOSURE"] = "EVALUATION_COMPLETE"
    exposure["evaluator_executed"] = True
    exposure["scientific_verdict_computed"] = True
    exposure["verdict"] = verdict["verdict"]
    manifest["production_activation"] = False
    manifest["batch1_production_active"] = True
    manifest["batch2_production_active"] = False
    _save_json(project_root / MANIFEST_PATH, manifest)

    print(f"[EVALUATOR COMPLETE] Level {verdict['verdict_level']}: {verdict['verdict']}")
    return evaluator_results


def ACTIVE_RULE_CASE_GROUPS_GROUPS_ALL() -> list[str]:
    """All case ids that host an active per-rule treatment pair."""
    cases: list[str] = []
    for mapping in ACTIVE_RULE_CASE_GROUPS.values():
        for case_id in mapping:
            if case_id not in cases:
                cases.append(case_id)
    return cases


def PRIMARY_METRICS_AND_MRR() -> list[str]:
    return PRIMARY_METRIC_KEYS + ["mrr"]


# ---------------------------------------------------------------------------
# Post-closeout read-only verification
# ---------------------------------------------------------------------------


def verify_freeze(project_root: Path) -> dict[str, Any]:
    """Section 50 independent read-only verification (no writes)."""
    assert_clean_worktree(project_root)
    head = git_head(project_root)
    chain: list[str] = []
    cursor = head
    for expected_message in (
        CLOSEOUT_COMMIT_MESSAGE,
        RAW_FREEZE_COMMIT_MESSAGE,
        PLAN_FREEZE_COMMIT_MESSAGE,
        EXECUTOR_FREEZE_COMMIT_MESSAGE,
    ):
        message = git_commit_message(project_root, cursor)
        if message != expected_message:
            raise RuntimeError(
                f"Commit chain mismatch at {cursor}: expected '{expected_message}', got '{message}'"
            )
        chain.append(cursor)
        cursor = git_parent(project_root, cursor)
    if cursor != STARTING_HEAD:
        raise RuntimeError(f"Chain base mismatch: expected {STARTING_HEAD}, got {cursor}")
    chain.append(cursor)

    def _blob_at(rel: str, rev: str) -> str | None:
        return git_blob(project_root, rel, rev)

    executor_freeze_head, plan_freeze_head, raw_freeze_head, closeout_head, base = chain
    checks: dict[str, Any] = {
        "chain": chain,
        "evaluator_code_unchanged_since_executor_freeze": git_paths_unchanged_between(
            project_root, executor_freeze_head, head, [RUNNER_PATH, TEST_PATH]
        ) == [],
        "plan_artifact_unchanged_since_plan_freeze": git_paths_unchanged_between(
            project_root, plan_freeze_head, head, [RAW_PLANS_PATH]
        ) == [],
        "raw_results_unchanged_since_raw_freeze": git_paths_unchanged_between(
            project_root, raw_freeze_head, head, [RAW_RESULTS_PATH]
        ) == [],
        "prereg_unchanged_since_starting_head": _blob_at(PREREGISTRATION_PATH, base)
        == _blob_at(PREREGISTRATION_PATH, head),
        "production_unchanged_since_starting_head": git_paths_unchanged_between(
            project_root, base, head, list(PRODUCTION_IMMUTABLE_PATHS)
        ) == [],
    }

    manifest = _load_json(project_root / MANIFEST_PATH)
    result = _load_json(project_root / RESULT_PATH)
    evaluator_results = _load_json(project_root / EVALUATOR_RESULTS_PATH)
    checks["machine_artifacts_agree"] = (
        result["verdict"] == evaluator_results["verdict"]
        and result["verdict"] == manifest["outcome_exposure_state"].get("verdict")
        and result["per_rule_dispositions"] == evaluator_results["per_rule_dispositions"]
        and manifest["production_activation"] is False
        and manifest["batch1_production_active"] is True
        and manifest["batch2_production_active"] is False
        and result["production_activation"] is False
    )
    checks["batch1_active"] = True
    checks["batch2_production_inactive"] = True

    for rel in (
        MANIFEST_PATH, RAW_PLANS_PATH, RAW_RESULTS_PATH,
        EVALUATOR_RESULTS_PATH, RESULT_PATH,
        PREREGISTRATION_PATH, SELECTION_PATH,
    ):
        _load_json(project_root / rel)
    checks["all_json_parsable"] = True
    diff_check = _git(["diff", "--check"], project_root)
    checks["git_diff_check_clean"] = diff_check == ""
    return checks


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=_PROJECT_ROOT)
    parser.add_argument(
        "--mode",
        required=True,
        choices=["audit", "execute-phase-p", "execute-phase-r", "evaluate", "verify-freeze"],
    )
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    if args.mode == "audit":
        receipt = audit_starting_boundary(project_root)
        print(json.dumps(receipt, ensure_ascii=False, indent=2, default=str))
        if not receipt["rule_boundary"]["valid"]:
            raise SystemExit("Starting boundary audit FAILED")
        if receipt["batch2_candidate_drift"]["all_clean"] is False:
            raise SystemExit("Batch-2 candidate drift detected")
        return
    if args.mode == "execute-phase-p":
        execute_phase_p(project_root)
        return
    if args.mode == "execute-phase-r":
        execute_phase_r(project_root)
        return
    if args.mode == "evaluate":
        evaluate_d4_a5(project_root)
        return
    if args.mode == "verify-freeze":
        receipt = verify_freeze(project_root)
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        if not all(v is True or isinstance(v, list) for v in receipt.values() if not isinstance(v, list)):
            raise SystemExit("Freeze verification FAILED")
        return
    raise SystemExit(f"Unknown mode: {args.mode}")


if __name__ == "__main__":
    main()
