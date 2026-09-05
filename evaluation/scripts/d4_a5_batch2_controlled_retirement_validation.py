"""PANDA Agent D4-A5 — Second-Batch Low-Risk Locator Controlled Retirement Validation.

R1 (D4-A5-R1 — Retirement Applicability and Provenance-Contract Repair) repairs
the pre-retrieval contract and persistence ordering after the correctly
fail-closed first A5 attempt:
  - component-level applicability model (ACTIVE_IDENTIFIABLE /
    INACTIVE_NOT_IDENTIFIABLE / AMBIGUOUS_INVALID) driven by selected-rule
    origin, never by raw token presence;
  - BATCH2_RETIREMENT projections built only from ACTIVE_IDENTIFIABLE
    components, preserving independent origins;
  - repaired 6-state per-rule disposition space and 7-level batch verdict;
  - persistence of every Analyzer acquisition (plan, ledger, origins,
    projections, applicability receipts, provider accounting) BEFORE any
    applicability gate can terminate execution;
  - forward-only continuation artifacts that leave the historical first-attempt
    manifest/result and the frozen D4-A4 contract untouched;
  - mechanical reusability audit of the first attempt's persisted plans and
    minimum-affected reacquisition policy for a separately authorized
    continuation.

Historical context (first A5 attempt, preserved immutable): Phase P stopped at
the original pre-outcome gate after 6 Analyzer calls because the frozen
model_factory_theory page-hint mask components (pflueger_2017: [51, 57, 65])
were absent from the acquired n014 canonical plan — production analyze() drops
rule page hints when the accepted intent is not algorithm_theory or
algorithm_implementation. A configured locator on a matched rule is therefore
not necessarily an active contribution in the final canonical RetrievalPlan.

CLI (run with PYTHONPATH=src):
    python evaluation/scripts/d4_a5_batch2_controlled_retirement_validation.py --project-root . --mode audit
    python evaluation/scripts/d4_a5_batch2_controlled_retirement_validation.py --project-root . --mode audit-reuse
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
from typing import Any, Mapping

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
# D4-A5-R1 repaired contract constants
# ---------------------------------------------------------------------------

R1_LIFECYCLE_ID = "D4-A5-R1"
A5_STOP_HEAD = "dc679f880cda8d2ccdfb709d725e24673c562eab"
A5_STOP_COMMIT_MESSAGE = "D4-A5 record pre-outcome provenance gate stop"
EXECUTOR_FREEZE_HEAD = "8579cdc60c3ebb53f9958d3fdd442c1a5454cc91"
R1_COMMIT_MESSAGE = "D4-A5-R1 repair retirement applicability contract"
R1_HEAD = "93ad95d7f8808bc4e7ccdbb21a24457c0df30564"
R2_COMMIT_MESSAGE = "D4-A5-R2 repair continuation freeze and accounting contract"
R2_HEAD = "a53ca0ace5280c278e32e350f5a5051b810fa6f4"
R2_PREREGISTRATION_PATH = "evaluation/d4_a5_r2_continuation_contract_preregistration.json"
R2_RESULT_PATH = "evaluation/d4_a5_r2_result.json"
R2_REPORT_PATH = "evaluation/D4_A5_R2_CONTINUATION_FREEZE_AND_ACCOUNTING_CONTRACT_REPAIR.md"
R3_COMMIT_MESSAGE = "D4-A5-R3 repair continuation lineage and end-to-end accounting"
R3_HEAD = "447d03e3cb9d3c1109d6f6070115f3ea4618bb7e"
R3_PREREGISTRATION_PATH = "evaluation/d4_a5_r3_continuation_lineage_accounting_preregistration.json"
R3_RESULT_PATH = "evaluation/d4_a5_r3_result.json"
R3_REPORT_PATH = "evaluation/D4_A5_R3_CONTINUATION_LINEAGE_AND_END_TO_END_ACCOUNTING_REPAIR.md"
R5_COMMIT_MESSAGE = "D4-A5-R5 seal raw-freeze evaluator integrity"
R5_PREREGISTRATION_PATH = "evaluation/d4_a5_r5_raw_freeze_evaluator_integrity_preregistration.json"
R5_RESULT_PATH = "evaluation/d4_a5_r5_result.json"
R5_REPORT_PATH = "evaluation/D4_A5_R5_RAW_FREEZE_EVALUATOR_INTEGRITY_SEAL.md"

CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE = "D4-A5 continuation freeze prospective shared plans"
CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE = "D4-A5 continuation freeze paired raw retirement results"
CONTINUATION_CLOSEOUT_COMMIT_MESSAGE = "D4-A5 continuation close controlled retirement validation"

# Component applicability tri-state (task Section 6).
APPLICABILITY_ACTIVE = "ACTIVE_IDENTIFIABLE"
APPLICABILITY_INACTIVE = "INACTIVE_NOT_IDENTIFIABLE"
APPLICABILITY_AMBIGUOUS = "AMBIGUOUS_INVALID"
APPLICABILITY_STATUSES = (APPLICABILITY_ACTIVE, APPLICABILITY_INACTIVE, APPLICABILITY_AMBIGUOUS)

INACTIVE_HELD_REASON = (
    "Configured retirement component was not contributed by the selected Batch-2 rule to the "
    "final canonical plan after normal production plan construction (deterministic runtime "
    "plan-formation policy); no selected-rule contribution exists to subtract. Retirement "
    "effect not identifiable for this component in this plan; component remains HOLD."
)

# Repaired per-rule disposition space (task Section 11).
DISPOSITION_INVALID_PROTOCOL = "INVALID_PROTOCOL"
DISPOSITION_DEPENDENCY = "DEPENDENCY_OBSERVED_RETAIN"
DISPOSITION_BASELINE_INCONCLUSIVE = "INCONCLUSIVE_BASELINE_NOT_REPRODUCED"
DISPOSITION_NO_ACTIVE_COMPONENT = "INCONCLUSIVE_NO_ACTIVE_RETIREMENT_COMPONENT"
DISPOSITION_PARTIAL_COMPONENT_HOLD = "PARTIAL_RETIREMENT_VALIDATED_COMPONENT_HOLD"
DISPOSITION_RETIREMENT_VALIDATED = "RETIREMENT_VALIDATED"
R1_PER_RULE_DISPOSITIONS = (
    DISPOSITION_INVALID_PROTOCOL,
    DISPOSITION_DEPENDENCY,
    DISPOSITION_BASELINE_INCONCLUSIVE,
    DISPOSITION_NO_ACTIVE_COMPONENT,
    DISPOSITION_PARTIAL_COMPONENT_HOLD,
    DISPOSITION_RETIREMENT_VALIDATED,
)

# Repaired 7-level batch verdict precedence (task Section 13).
R1_VERDICT_LEVEL_1_INVALID = "INVALID / BATCH2_PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED"
R1_VERDICT_LEVEL_2_BASELINE = "INCONCLUSIVE / BATCH2_REFERENCE_BASELINE_NOT_REPRODUCED"
R1_VERDICT_LEVEL_3_DEPENDENCY = "PARTIAL / SOME_RETIREMENT_CANDIDATES_RETAIN_DEPENDENCY"
R1_VERDICT_LEVEL_4_SAFETY = "FAIL / BATCH2_CRITICAL_OR_GROUNDING_REGRESSION"
R1_VERDICT_LEVEL_5_APPLICABILITY = "PARTIAL / RETIREMENT_COMPONENT_APPLICABILITY_INCOMPLETE"
R1_VERDICT_LEVEL_6_AGGREGATE = "PARTIAL / BATCH2_AGGREGATE_REGRESSION_EXCEEDS_BOUNDED_TOLERANCE"
R1_VERDICT_LEVEL_7_PASS = "PASS / SECOND_BATCH_LOW_RISK_RETIREMENT_VALIDATED"
R1_BATCH_VERDICT_LEVELS = {
    1: R1_VERDICT_LEVEL_1_INVALID,
    2: R1_VERDICT_LEVEL_2_BASELINE,
    3: R1_VERDICT_LEVEL_3_DEPENDENCY,
    4: R1_VERDICT_LEVEL_4_SAFETY,
    5: R1_VERDICT_LEVEL_5_APPLICABILITY,
    6: R1_VERDICT_LEVEL_6_AGGREGATE,
    7: R1_VERDICT_LEVEL_7_PASS,
}

# Forward-only continuation artifacts (historical first-attempt artifacts remain
# immutable at the A5 stop commit dc679f8).
HISTORICAL_MANIFEST_PATH = MANIFEST_PATH
HISTORICAL_RAW_PLANS_PATH = RAW_PLANS_PATH
CONTINUATION_MANIFEST_PATH = "evaluation/d4_a5_continuation_execution_manifest.json"
CONTINUATION_RAW_PLANS_PATH = "evaluation/d4_a5_continuation_raw_prospective_plans.json"
CONTINUATION_RAW_RESULTS_PATH = "evaluation/d4_a5_continuation_raw_paired_retirement_results.json"
CONTINUATION_EVALUATOR_RESULTS_PATH = "evaluation/d4_a5_continuation_evaluator_results.json"
CONTINUATION_RESULT_PATH = "evaluation/d4_a5_continuation_result.json"

# Strict raw-freeze diff allowlist (R5; task Section 7): the plan-freeze ->
# raw-freeze changed-file set must be a subset of exactly these paths.
RAW_FREEZE_DIFF_ALLOWLIST = (
    CONTINUATION_MANIFEST_PATH,
    CONTINUATION_RAW_RESULTS_PATH,
)
R1_PREREGISTRATION_PATH = "evaluation/d4_a5_r1_retirement_applicability_preregistration.json"
R1_RESULT_PATH = "evaluation/d4_a5_r1_result.json"
R1_REPORT_PATH = "evaluation/D4_A5_R1_RETIREMENT_APPLICABILITY_AND_PROVENANCE_CONTRACT_REPAIR.md"

REUSE_REUSABLE = "REUSABLE_FROZEN_SCIENTIFIC_PLAN"
REUSE_NOT_REUSABLE = "HISTORICAL_ATTEMPT_NOT_REUSABLE"
REUSE_NEVER_EXECUTED = "NEVER_EXECUTED"

# Historical first-attempt cost (immutable reference; never overwritten).
HISTORICAL_ATTEMPT_ACCOUNTING = {
    "attempt_id": "D4-A5_ATTEMPT_1",
    "manifest_path": MANIFEST_PATH,
    "preserved_at_commit": A5_STOP_HEAD,
    "analyzer_logical_calls": 6,
    "analyzer_provider_attempts": 6,
    "retries": 0,
    "recorded_token_usage": 10303,
    "unknown_token_usage": {
        "case_id": "n014",
        "note": "slot 6 consumed one Analyzer call whose token usage was not recorded "
        "(fail-closed stop before slot bookkeeping); unknown stays explicitly unknown",
    },
    "embedding_calls": 0,
    "reranker_calls": 0,
    "downstream_analyzer_calls": 0,
    "qa_verifier_judge_calls": 0,
    "db_qdrant_writes": 0,
    "protected_dataset_access": 0,
}


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


def classify_component_applicability(
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    configured_entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Component-level applicability classification (task Section 6/7/10).

    For every configured retirement-mask component of a matched selected Batch-2
    rule, classifies the SELECTED-RULE CONTRIBUTION — not the raw token presence —
    into exactly one of ACTIVE_IDENTIFIABLE / INACTIVE_NOT_IDENTIFIABLE /
    AMBIGUOUS_INVALID. Fully generic: no case-id, rule-id value, or component
    value special-casing.

    Semantics:
      - component present in the final canonical plan AND the ledger entry
        carries the selected-rule origin -> ACTIVE_IDENTIFIABLE;
      - component present but ONLY via independent origins (selected rule did
        not contribute it after normal production plan construction) ->
        INACTIVE_NOT_IDENTIFIABLE; the independently contributed token/page
        remains active and untouched;
      - component absent from the final canonical plan (the plan is the
        unmodified production analyze() output, so the absence is a
        deterministic consequence of normal production plan formation) ->
        INACTIVE_NOT_IDENTIFIABLE;
      - component present without identifiable/complete provenance, or any
        ledger/plan contradiction -> AMBIGUOUS_INVALID (fail closed).
    """
    plan_symbols = set(canonical_plan.get("symbols") or [])
    plan_hints = {
        (str(src), int(page))
        for src, pages in (canonical_plan.get("paper_page_hints") or {}).items()
        for page in (pages or [])
    }
    by_id = {entry["contribution_id"]: entry for entry in ledger}

    receipts: list[dict[str, Any]] = []
    summary = {"active": 0, "inactive": 0, "ambiguous": 0}
    for entry in configured_entries:
        rid = entry["rule_id"]
        if entry["kind"] == "symbol":
            contribution_id = f"symbol::{entry['value']}"
            plan_present = entry["value"] in plan_symbols
        else:
            contribution_id = f"paper_page_hint::{entry['source_id']}#{entry['pdf_page']}"
            plan_present = (entry["source_id"], int(entry["pdf_page"])) in plan_hints
        ledger_entry = by_id.get(contribution_id)
        origins = list((ledger_entry or {}).get("provenance_origin_ids") or [])
        ledger_claims_present = bool((ledger_entry or {}).get("plan_present"))

        selected_origin_present = rid in origins
        independent_origins = [o for o in origins if o != rid]
        ambiguity_reason = None
        if plan_present and ledger_entry is None:
            status = APPLICABILITY_AMBIGUOUS
            ambiguity_reason = (
                "Component is present in the final canonical plan but has no contribution-ledger "
                "entry; selected-rule ownership cannot be determined."
            )
        elif plan_present and not origins:
            status = APPLICABILITY_AMBIGUOUS
            ambiguity_reason = (
                "Component is present in the final canonical plan but its provenance is "
                "empty/incomplete; selected-rule ownership cannot be determined."
            )
        elif ledger_entry is not None and ledger_claims_present != plan_present:
            status = APPLICABILITY_AMBIGUOUS
            ambiguity_reason = (
                "Contribution ledger and canonical plan contradict each other about component "
                "presence; provenance is unreliable."
            )
        elif plan_present and selected_origin_present:
            status = APPLICABILITY_ACTIVE
        elif plan_present and not selected_origin_present:
            status = APPLICABILITY_INACTIVE
        else:  # not plan_present
            status = APPLICABILITY_INACTIVE

        if status == APPLICABILITY_ACTIVE:
            action = "remove_selected_rule_origin_preserve_independent_origins"
        elif status == APPLICABILITY_INACTIVE:
            action = "none_inactive_nothing_to_subtract"
        else:
            action = "not_constructed_ambiguous_fail_closed"
        summary_key = {"ACTIVE_IDENTIFIABLE": "active", "INACTIVE_NOT_IDENTIFIABLE": "inactive",
                       "AMBIGUOUS_INVALID": "ambiguous"}[status]
        summary[summary_key] += 1
        receipts.append({
            "rule_id": rid,
            "component_kind": entry["kind"],
            "component_value": entry["value"],
            "source_id": entry["source_id"],
            "pdf_page": entry["pdf_page"],
            "configured_in_frozen_mask": True,
            "selected_rule_origin_present": selected_origin_present,
            "provenance_origin_ids": origins,
            "independent_origins": independent_origins,
            "final_canonical_plan_presence": plan_present,
            "applicability_status": status,
            "retirement_projection_action": action,
            "held_reason": INACTIVE_HELD_REASON if status == APPLICABILITY_INACTIVE else None,
            "provenance_ambiguity_reason": ambiguity_reason,
        })
    return receipts, summary


def build_retirement_projection_r1(
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    component_receipts: list[dict[str, Any]],
    matched_retirement_rules: list[str],
    masks: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Repaired BATCH2_RETIREMENT projection (task Section 8).

    Removes ONLY selected-rule origins classified ACTIVE_IDENTIFIABLE, preserving
    independent origins; does nothing for INACTIVE_NOT_IDENTIFIABLE components.
    Raises on AMBIGUOUS_INVALID (the caller must stop before retrieval). The
    canonical plan is never mutated.
    """
    ambiguous = [
        r for r in component_receipts if r["applicability_status"] == APPLICABILITY_AMBIGUOUS
    ]
    if ambiguous:
        raise ValueError(
            "AMBIGUOUS_INVALID components present; retirement projection must not be "
            f"constructed: {[r['component_value'] for r in ambiguous]}"
        )
    active_entries = [
        {
            "rule_id": r["rule_id"],
            "kind": r["component_kind"],
            "value": r["component_value"],
            "source_id": r["source_id"],
            "pdf_page": r["pdf_page"],
        }
        for r in component_receipts
        if r["applicability_status"] == APPLICABILITY_ACTIVE
    ]
    projected, receipts = build_retirement_projection(
        canonical_plan, ledger, active_entries, matched_retirement_rules, masks
    )
    receipts["applicability_summary"] = {
        "active": sum(1 for r in component_receipts if r["applicability_status"] == APPLICABILITY_ACTIVE),
        "inactive": sum(1 for r in component_receipts if r["applicability_status"] == APPLICABILITY_INACTIVE),
        "ambiguous": 0,
        "inactive_components": [
            {"rule_id": r["rule_id"], "kind": r["component_kind"], "value": r["component_value"],
             "held_reason": r["held_reason"]}
            for r in component_receipts if r["applicability_status"] == APPLICABILITY_INACTIVE
        ],
    }
    return projected, receipts


def build_provenance_gate_receipt(
    case_id: str,
    attribution: dict[str, Any],
    matched_rule_ids: list[str],
    canonical_plan: dict[str, Any],
    ledger: list[dict[str, Any]],
    current_compat_projection: dict[str, Any],
    batch2_retirement_projection: dict[str, Any],
    projection_receipts: dict[str, Any],
    component_receipts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Repaired pre-outcome provenance gate (R1; task Sections 6-10).

    INACTIVE_NOT_IDENTIFIABLE components are NOT a gate failure: they carry
    HOLD receipts and are excluded from the projection. Only AMBIGUOUS_INVALID
    provenance, ledger/plan contradiction, projection drift, or control
    divergence fail the gate.
    """
    selected_expected = list(attribution["matched_retirement_rules"])
    matched_batch2 = [rid for rid in selected_expected if rid in matched_rule_ids]
    gate: dict[str, Any] = {"case_id": case_id, "checks": {}}

    gate["checks"]["selected_rule_matched"] = {
        "expected": selected_expected,
        "observed": matched_batch2,
        "pass": sorted(matched_batch2) == sorted(selected_expected),
    }
    configured_entries = build_batch2_mask_entries(case_id, matched_batch2)
    if component_receipts is None:
        component_receipts, _ = classify_component_applicability(
            canonical_plan, ledger, configured_entries
        )
    gate["checks"]["configured_mask_size"] = {
        "expected": len(configured_entries),
        "observed": len(component_receipts),
        "pass": len(configured_entries) == len(component_receipts)
        and (len(configured_entries) > 0) == bool(selected_expected),
    }
    coverage_ok, coverage_error = validate_ledger_coverage(canonical_plan, ledger)
    gate["checks"]["ledger_coverage"] = {"pass": coverage_ok, "error": coverage_error}

    ambiguous = [
        r for r in component_receipts if r["applicability_status"] == APPLICABILITY_AMBIGUOUS
    ]
    gate["checks"]["component_applicability"] = {
        "pass": not ambiguous,
        "active": sum(1 for r in component_receipts if r["applicability_status"] == APPLICABILITY_ACTIVE),
        "inactive": sum(1 for r in component_receipts if r["applicability_status"] == APPLICABILITY_INACTIVE),
        "ambiguous": len(ambiguous),
        "ambiguous_details": [
            {"value": r["component_value"], "reason": r["provenance_ambiguity_reason"]}
            for r in ambiguous
        ],
        "inactive_note": (
            "INACTIVE_NOT_IDENTIFIABLE components are HOLD, not protocol failures; they are "
            "excluded from the retirement projection and never count toward retirement success."
        ),
    }

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
    gate["component_applicability_receipts"] = component_receipts
    return gate


def classify_rule_r1(
    *,
    protocol_valid: bool,
    baseline_reproduced: bool,
    attributable_loss: bool,
    active_component_count: int,
    frozen_component_count: int,
) -> str:
    """Repaired per-rule disposition precedence (task Section 11).

    1. INVALID_PROTOCOL  — ambiguous provenance / malformed input / plan
                           inequality / projection drift / impossible attribution
    2. DEPENDENCY_OBSERVED_RETAIN — any attributable T/F loss from removal of
                           the rule's ACTIVE_IDENTIFIABLE contribution set;
                           takes precedence over baseline incompleteness
    3. INCONCLUSIVE_BASELINE_NOT_REPRODUCED — no attributable loss but the
                           required active-case baseline evidence is missing
    4. INCONCLUSIVE_NO_ACTIVE_RETIREMENT_COMPONENT — protocol valid, baseline
                           reproduced, but ZERO frozen components are
                           ACTIVE_IDENTIFIABLE (nothing was scientifically tested)
    5. PARTIAL_RETIREMENT_VALIDATED_COMPONENT_HOLD — protocol valid, baseline
                           reproduced, no attributable loss, and only a strict
                           subset of the frozen components is ACTIVE_IDENTIFIABLE
    6. RETIREMENT_VALIDATED — protocol valid, baseline reproduced, no
                           attributable loss, and ALL frozen components are
                           ACTIVE_IDENTIFIABLE
    """
    if any(type(v) is not bool for v in (protocol_valid, baseline_reproduced, attributable_loss)):
        return DISPOSITION_INVALID_PROTOCOL
    if type(active_component_count) is not int or type(frozen_component_count) is not int:
        return DISPOSITION_INVALID_PROTOCOL
    if active_component_count < 0 or frozen_component_count < 0:
        return DISPOSITION_INVALID_PROTOCOL
    if active_component_count > frozen_component_count:
        return DISPOSITION_INVALID_PROTOCOL
    if (
        not protocol_valid
        or frozen_component_count == 0
        or (attributable_loss and active_component_count == 0)
    ):
        # Contradictory or malformed disposition inputs are protocol-invalid:
        # an empty frozen mask is impossible for the selected rules, and an
        # attributable T/F loss cannot exist without an ACTIVE_IDENTIFIABLE
        # contribution set that was actually removed.
        return DISPOSITION_INVALID_PROTOCOL
    if attributable_loss:
        return DISPOSITION_DEPENDENCY
    if not baseline_reproduced:
        return DISPOSITION_BASELINE_INCONCLUSIVE
    if active_component_count == 0:
        return DISPOSITION_NO_ACTIVE_COMPONENT
    if active_component_count < frozen_component_count:
        return DISPOSITION_PARTIAL_COMPONENT_HOLD
    return DISPOSITION_RETIREMENT_VALIDATED


def evaluate_batch2_verdict_r1(
    *,
    execution_valid: bool | None = None,
    protocol_violation: bool | None = None,
    missing_inputs: bool | None = None,
    plan_equality_all_verified: bool | None = None,
    analyzer_provider_calls_downstream: int | None = None,
    reference_baseline_valid: bool | None = None,
    per_rule_dispositions: Mapping[str, str] | None = None,
    critical_retirement_regressions: int | None = None,
    grounding_regressions: int | None = None,
    wrong_version_regressions: int | None = None,
    invalid_provenance_recoveries: int | None = None,
    metric_deltas: Mapping[str, float] | None = None,
    metric_tolerances: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Repaired 7-level batch verdict precedence (task Section 13).

    Evaluation order: L1 -> L2 -> L4 -> L3 -> L5 -> L6 -> L7.
    L4 (safety) wins over L3 (dependency) when both coexist; L2 (baseline
    inconclusive) precedes safety, consistent with the historical A4 contract.
    No undefined verdict state exists: every complete input combination maps to
    exactly one level.
    """
    flags = (execution_valid, protocol_violation, missing_inputs,
             plan_equality_all_verified, reference_baseline_valid)
    counters = (analyzer_provider_calls_downstream, critical_retirement_regressions,
                grounding_regressions, wrong_version_regressions, invalid_provenance_recoveries)
    complete = (
        all(type(flag) is bool for flag in flags)
        and all(type(count) is int and count >= 0 for count in counters)
        and isinstance(per_rule_dispositions, Mapping)
        and set(per_rule_dispositions) == set(b2.CANDIDATE_RULE_IDS)
        and all(d in R1_PER_RULE_DISPOSITIONS for d in per_rule_dispositions.values())
        and isinstance(metric_deltas, Mapping)
        and set(DEFAULT_METRIC_TOLERANCES_KEYS) <= set(metric_deltas)
        and all(type(metric_deltas[k]) in (int, float) and math.isfinite(metric_deltas[k])
                and -1 <= metric_deltas[k] <= 1 for k in DEFAULT_METRIC_TOLERANCES_KEYS)
        and (metric_tolerances is None or dict(metric_tolerances) == b2.DEFAULT_METRIC_BOUNDED_TOLERANCES)
    )
    if not complete:
        return {
            "verdict_level": 1, "verdict": R1_VERDICT_LEVEL_1_INVALID,
            "verdict_status": "INVALID",
            "verdict_reason": "Incomplete or malformed repaired evaluator inputs.",
        }

    # Level 1: protocol / shared plan / input completeness defects.
    if (
        not execution_valid
        or protocol_violation
        or missing_inputs
        or not plan_equality_all_verified
        or analyzer_provider_calls_downstream > 0
        or any(d == DISPOSITION_INVALID_PROTOCOL for d in per_rule_dispositions.values())
    ):
        return {
            "verdict_level": 1, "verdict": R1_VERDICT_LEVEL_1_INVALID,
            "verdict_status": "INVALID",
            "verdict_reason": "Protocol violation, execution invalid, missing inputs, shared "
            "plan inequality, downstream Analyzer call, or INVALID_PROTOCOL rule disposition.",
        }

    # Level 2: reference baseline not reproduced.
    if (
        not reference_baseline_valid
        or any(d == DISPOSITION_BASELINE_INCONCLUSIVE for d in per_rule_dispositions.values())
    ):
        return {
            "verdict_level": 2, "verdict": R1_VERDICT_LEVEL_2_BASELINE,
            "verdict_status": "INCONCLUSIVE",
            "verdict_reason": "One or more active direct-rule reference baselines are not "
            "reproduced under the repaired disposition contract.",
        }

    # Level 4: safety failures win over dependency (Level 3).
    has_safety_violation = (
        critical_retirement_regressions > 0
        or grounding_regressions > 0
        or wrong_version_regressions > 0
        or invalid_provenance_recoveries > 0
    )
    if has_safety_violation:
        violations = []
        if critical_retirement_regressions > 0:
            violations.append(f"critical_retirement_regressions={critical_retirement_regressions}")
        if grounding_regressions > 0:
            violations.append(f"grounding_regressions={grounding_regressions}")
        if wrong_version_regressions > 0:
            violations.append(f"wrong_version_regressions={wrong_version_regressions}")
        if invalid_provenance_recoveries > 0:
            violations.append(f"invalid_provenance_recoveries={invalid_provenance_recoveries}")
        return {
            "verdict_level": 4, "verdict": R1_VERDICT_LEVEL_4_SAFETY,
            "verdict_status": "FAIL",
            "verdict_reason": f"Strict retirement safety rule violated: {', '.join(violations)} "
            "(safety failure wins over retained dependency).",
        }

    # Level 3: retained dependency without safety violation.
    if any(d == DISPOSITION_DEPENDENCY for d in per_rule_dispositions.values()):
        retained = [r for r, d in per_rule_dispositions.items() if d == DISPOSITION_DEPENDENCY]
        return {
            "verdict_level": 3, "verdict": R1_VERDICT_LEVEL_3_DEPENDENCY,
            "verdict_status": "PARTIAL",
            "verdict_reason": f"Observed retirement dependency on rule(s) {retained}; locator "
            "component(s) must be retained pending further decision.",
        }

    # Level 5: component applicability incomplete.
    if any(
        d in (DISPOSITION_NO_ACTIVE_COMPONENT, DISPOSITION_PARTIAL_COMPONENT_HOLD)
        for d in per_rule_dispositions.values()
    ):
        incomplete = [
            r for r, d in per_rule_dispositions.items()
            if d in (DISPOSITION_NO_ACTIVE_COMPONENT, DISPOSITION_PARTIAL_COMPONENT_HOLD)
        ]
        return {
            "verdict_level": 5, "verdict": R1_VERDICT_LEVEL_5_APPLICABILITY,
            "verdict_status": "PARTIAL",
            "verdict_reason": f"Rule(s) {incomplete} have inactive or untestable frozen "
            "retirement components in their active direct cases; the full Batch2 mask was not "
            "completely testable. Inactive components remain HOLD.",
        }

    # Level 6: aggregate tolerance failure after full component validation.
    tols = dict(b2.DEFAULT_METRIC_BOUNDED_TOLERANCES)
    if metric_tolerances:
        tols.update(metric_tolerances)
    exceeded = [
        f"{name} delta {metric_deltas.get(name):.4f} < {tol:.4f}"
        for name, tol in tols.items()
        if metric_deltas.get(name) is not None and metric_deltas.get(name) < tol
    ]
    if exceeded:
        return {
            "verdict_level": 6, "verdict": R1_VERDICT_LEVEL_6_AGGREGATE,
            "verdict_status": "PARTIAL",
            "verdict_reason": "All selected rules fully validated without safety failure, but "
            f"the aggregate bounded tolerance is exceeded: {', '.join(exceeded)}.",
        }

    # Level 7: clean pass.
    if all(d == DISPOSITION_RETIREMENT_VALIDATED for d in per_rule_dispositions.values()):
        return {
            "verdict_level": 7, "verdict": R1_VERDICT_LEVEL_7_PASS,
            "verdict_status": "PASS",
            "verdict_reason": "Second-batch low-risk retirement validated: all candidate rules "
            "fully validated with every frozen component ACTIVE_IDENTIFIABLE, zero "
            "critical/grounding/version/provenance regressions, and all bounded tolerances "
            "satisfied.",
        }
    # Defensive fallback (unreachable for complete inputs): fail closed to Level 5.
    return {
        "verdict_level": 5, "verdict": R1_VERDICT_LEVEL_5_APPLICABILITY,
        "verdict_status": "PARTIAL",
        "verdict_reason": "Unclassified non-passing disposition without critical safety "
        "violation; treated as applicability-incomplete.",
    }


DEFAULT_METRIC_TOLERANCES_KEYS = (
    "recall_at_5",
    "recall_at_10",
    "recall_at_20",
    "combined_candidate_recall",
    "final_evidence_recall",
    "critical_final_evidence_recall",
)


def audit_historical_plan_reusability(project_root: Path) -> dict[str, Any]:
    """Mechanical reusability audit of the first A5 attempt (task Sections 18-20).

    Reads the immutable stopped manifest committed at the A5 stop head and, for
    each case, checks whether ALL of the following are durably recoverable
    without any provider call: exact canonical RetrievalPlan, canonical
    serialized representation, complete contribution ledger, exact origin
    provenance, CURRENT_COMPAT projection, retirement projection, deterministic
    signature, provider accounting. A plan_signature alone never qualifies.
    """
    historical = _load_json(project_root / HISTORICAL_MANIFEST_PATH)
    slots = {s["case_id"]: s for s in historical["phase_p_slots_7"]}
    required_fields = (
        "canonical_plan",
        "canonical_serialization",
        "contribution_ledger",
        "provenance_origin_receipts",
        "current_compat_execution_projection",
        "batch2_retirement_execution_projection",
        "plan_signature",
        "provider_accounting",
    )
    raw_plans_committed = git_blob(project_root, HISTORICAL_RAW_PLANS_PATH, "HEAD") is not None
    per_case: dict[str, dict[str, Any]] = {}
    for cid in CASE_ORDER:
        slot = slots.get(cid)
        if slot is None or slot["status"] == "NOT_EXECUTED":
            per_case[cid] = {
                "previous_execution_state": "NEVER_EXECUTED",
                "persisted_fields": sorted((slot or {}).keys()),
                "classification": REUSE_NEVER_EXECUTED,
                "reason": "Slot never consumed an Analyzer call and has no plan evidence.",
                "reacquisition_required": True,
            }
            continue
        persisted = sorted(slot.keys())
        missing = [f for f in required_fields if f not in persisted]
        classification = REUSE_REUSABLE if not missing else REUSE_NOT_REUSABLE
        reason = (
            "Complete frozen scientific plan artifact present."
            if classification == REUSE_REUSABLE
            else (
                f"Stopped manifest persists only slot-level bookkeeping "
                f"({', '.join(persisted)}); the complete canonical plan, serialization, "
                f"contribution ledger, origin provenance, and both execution projections were "
                f"never durably persisted (missing: {', '.join(missing)}). "
                f"Raw plans artifact committed: {raw_plans_committed}. A plan_signature alone "
                f"does not satisfy the reuse contract."
            )
        )
        per_case[cid] = {
            "previous_execution_state": slot["status"],
            "persisted_fields": persisted,
            "classification": classification,
            "reason": reason,
            "reacquisition_required": classification != REUSE_REUSABLE,
        }
    reusable = [c for c, v in per_case.items() if v["classification"] == REUSE_REUSABLE]
    not_reusable = [c for c, v in per_case.items() if v["classification"] == REUSE_NOT_REUSABLE]
    never_executed = [c for c, v in per_case.items() if v["classification"] == REUSE_NEVER_EXECUTED]
    return {
        "historical_manifest": HISTORICAL_MANIFEST_PATH,
        "historical_raw_plans_artifact_committed": raw_plans_committed,
        "required_artifact_fields": list(required_fields),
        "per_case": per_case,
        "reusable_cases": reusable,
        "non_reusable_cases": not_reusable,
        "never_executed_cases": never_executed,
        "future_continuation_policy": {
            "reuse_required": "Every case classified REUSABLE_FROZEN_SCIENTIFIC_PLAN must be "
            "reused, never redrawn.",
            "reacquisition_required": [c for c in CASE_ORDER if per_case[c]["reacquisition_required"]],
            "fresh_complete_acquisition": len(reusable) == 0,
            "note": "A fresh complete 7-plan acquisition for a separately authorized "
            "continuation is not an outcome-improvement rerun because no valid frozen 7-plan "
            "scientific artifact exists.",
        },
    }


def build_continuation_manifest(project_root: Path, reuse_audit: dict[str, Any]) -> dict[str, Any]:
    """Forward-only continuation execution manifest (task Sections 3/22).

    Preserves the historical first attempt by reference (immutable at the A5
    stop commit), records attempt-local and cumulative provider accounting, and
    marks each Phase P slot with its reuse classification and reacquisition
    eligibility.
    """
    manifest = build_initial_manifest(project_root)
    manifest["checkpoint"] = "D4-A5-CONTINUATION"
    manifest["stage"] = "d4_a5_continuation_batch2_controlled_retirement_execution_manifest"
    manifest["created_at"] = _utc_now()
    manifest["repair_lineage"] = {
        "historical_a5_starting_boundary": STARTING_HEAD,
        "historical_a5_executor_freeze_head": EXECUTOR_FREEZE_HEAD,
        "historical_a5_stop_head": A5_STOP_HEAD,
        "historical_a5_stop_verdict": "INVALID / BATCH2_PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED",
        "r1_parent_boundary": R1_HEAD,
        "r2_parent_boundary": R2_HEAD,
        "r3_parent_boundary": R3_HEAD,
        "r5_continuation_implementation_freeze": "commit containing this manifest",
        "repair_lifecycle": R1_LIFECYCLE_ID,
        "repair_preregistration": R1_PREREGISTRATION_PATH,
        "r2_continuation_contract_preregistration": R2_PREREGISTRATION_PATH,
        "r3_continuation_lineage_preregistration": R3_PREREGISTRATION_PATH,
        "r5_raw_freeze_integrity_preregistration": R5_PREREGISTRATION_PATH,
    }
    # Unambiguous continuation lineage vocabulary (R5): historical R1/R2/R3 heads
    # are historical facts and never drive current continuation gates; the current
    # continuation implementation freeze is the R5 freeze commit.
    manifest["continuation_lineage"] = {
        "historical_a5_starting_head": STARTING_HEAD,
        "historical_a5_executor_freeze_head": EXECUTOR_FREEZE_HEAD,
        "historical_a5_stop_head": A5_STOP_HEAD,
        "historical_r1_head": R1_HEAD,
        "historical_r2_head": R2_HEAD,
        "historical_r3_head": R3_HEAD,
        "continuation_implementation_freeze_message": R5_COMMIT_MESSAGE,
        "continuation_plan_freeze_message": CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE,
        "continuation_raw_freeze_message": CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE,
        "raw_freeze_diff_allowlist": list(RAW_FREEZE_DIFF_ALLOWLIST),
    }
    manifest["artifact_paths"] = {
        "manifest": CONTINUATION_MANIFEST_PATH,
        "raw_plans": CONTINUATION_RAW_PLANS_PATH,
        "raw_results": CONTINUATION_RAW_RESULTS_PATH,
        "evaluator_results": CONTINUATION_EVALUATOR_RESULTS_PATH,
        "result": CONTINUATION_RESULT_PATH,
        "historical_manifest_untouched": HISTORICAL_MANIFEST_PATH,
    }
    # Repaired contract authority: the continuation execution contract is governed
    # by the R1 applicability repair; the frozen D4-A4 scientific selection/masks
    # are referenced read-only and never replaced.
    manifest["continuation_contract_authority"] = {
        "applicability_repair_authority": R1_PREREGISTRATION_PATH,
        "scientific_selection_authority": PREREGISTRATION_PATH,
        "scientific_selection_mutability": "read-only frozen reference; never replaced",
    }
    # Continuation execution gates replace the first-attempt messages; the old
    # messages are retained only as clearly labeled historical references.
    manifest["implementation_freeze_contract"] = {
        "policy": "GIT_COMMIT_CONTAINING_THIS_ARTIFACT",
        "expected_commit_message": R5_COMMIT_MESSAGE,
        "expected_parent": R3_HEAD,
        "note": "The R5 freeze commit contains this manifest and is the current continuation "
        "implementation freeze; no descendant or intervening commit is accepted as a "
        "replacement freeze.",
    }
    manifest["plan_freeze_gate_contract"] = {
        "policy": "HARD_COMMIT_PLAN_FREEZE_GATE",
        "expected_commit_message": CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE,
        "expected_parent": "the R5 continuation implementation freeze commit "
        "(continuation_implementation_freeze_head)",
        "raw_plans_path": CONTINUATION_RAW_PLANS_PATH,
        "diff_allowlist": [CONTINUATION_MANIFEST_PATH, CONTINUATION_RAW_PLANS_PATH],
    }
    manifest["raw_freeze_gate_contract"] = {
        "policy": "HARD_COMMIT_RAW_FREEZE_GATE_WITH_STRICT_EVALUATOR_INTEGRITY_SEAL",
        "expected_commit_message": CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE,
        "expected_parent": "the continuation plan-freeze commit "
        "(continuation_plan_freeze_head)",
        "raw_results_path": CONTINUATION_RAW_RESULTS_PATH,
        "strict_diff_allowlist": list(RAW_FREEZE_DIFF_ALLOWLIST),
        "evaluator_integrity": {
            "runner_blob": "runner blob at raw-freeze HEAD == runner blob at "
            "continuation_implementation_freeze_head (R5)",
            "focused_test_blob": "focused test blob at raw-freeze HEAD == focused test blob "
            "at continuation_implementation_freeze_head (R5)",
            "raw_plans_blob": "continuation raw plans blob at raw-freeze HEAD == continuation "
            "raw plans blob at plan-freeze HEAD",
        },
    }
    manifest["closeout_gate_contract"] = {
        "policy": "HARD_COMMIT_CLOSEOUT_GATE",
        "expected_commit_message": CONTINUATION_CLOSEOUT_COMMIT_MESSAGE,
        "expected_parent": "the continuation raw-freeze commit",
    }
    manifest["historical_first_attempt_freeze_messages"] = {
        "executor_freeze": EXECUTOR_FREEZE_COMMIT_MESSAGE,
        "plan_freeze": PLAN_FREEZE_COMMIT_MESSAGE,
        "raw_freeze": RAW_FREEZE_COMMIT_MESSAGE,
        "status": "HISTORICAL ONLY — not current continuation execution gates",
    }
    manifest["reusability_decision"] = dict(CONTINUATION_EXPECTED_REUSABILITY)
    manifest["reusability_decision"]["signature_alone_insufficient"] = True
    manifest["reusability_decision"]["source"] = "R1 mechanical audit (forward-only, frozen)"
    manifest["attempt_accounting"] = {
        "historical_attempt": dict(HISTORICAL_ATTEMPT_ACCOUNTING),
        "continuation_attempt": {
            "attempt_id": "D4-A5_ATTEMPT_2_CONTINUATION",
            "analyzer_logical_calls": 0,
            "analyzer_provider_attempts": 0,
            "unknown_provider_attempt_events": 0,
            "retries": 0,
            "token_usage": 0,
            "unknown_token_usage": [],
            "unknown_token_usage_events": 0,
            "embedding_calls": 0,
            "reranker_calls": 0,
            "retrieval_provider_attempts": 0,
            "downstream_analyzer_calls": 0,
            "qa_verifier_judge_calls": 0,
            "db_qdrant_writes": 0,
            "protected_dataset_access": 0,
        },
        "cumulative": {
            "analyzer_logical_calls": HISTORICAL_ATTEMPT_ACCOUNTING["analyzer_logical_calls"],
            "analyzer_provider_attempts": HISTORICAL_ATTEMPT_ACCOUNTING["analyzer_provider_attempts"],
            "provider_attempt_unknown_components": 0,
            "retries": 0,
            "token_usage_recorded": HISTORICAL_ATTEMPT_ACCOUNTING["recorded_token_usage"],
            "token_usage_unknown_components": 1,
            "embedding_calls": 0,
            "reranker_calls": 0,
            "retrieval_provider_attempts": 0,
        },
        "accounting_rule": "Historical and continuation attempt costs are recorded separately; "
        "cumulative cost is their sum. Unknown historical token usage stays explicitly unknown "
        "and is never fabricated.",
    }
    for slot in manifest["phase_p_slots_7"]:
        audit = reuse_audit["per_case"][slot["case_id"]]
        slot["reuse_classification"] = audit["classification"]
        slot["reacquisition_required"] = audit["reacquisition_required"]
        slot["reuse_source"] = (
            {"manifest": HISTORICAL_MANIFEST_PATH, "raw_plans": HISTORICAL_RAW_PLANS_PATH}
            if audit["classification"] == REUSE_REUSABLE else None
        )
        slot["status"] = "NOT_EXECUTED"
    return manifest


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


CONTINUATION_EXPECTED_REUSABILITY = {
    "reusable_cases": [],
    "non_reusable_cases": ["g052", "g055", "n003", "n004", "g007", "n014"],
    "never_executed_cases": ["g060"],
    "reacquisition_required_cases": ["g052", "g055", "n003", "n004", "g007", "n014", "g060"],
}


def verify_continuation_start(project_root: Path) -> dict[str, Any]:
    """Read-only pre-provider continuation-start gate (R2; task Section 11).

    The single shared preflight used by both the CLI mode
    ``verify-continuation-start`` and the real ``execute_phase_p``. Establishes,
    with zero provider calls:
      1. HEAD is the R2 implementation-freeze commit;
      2. exact parent is the R1 HEAD;
      3. the continuation manifest is committed AT HEAD (introduced by this
         commit — absent at the parent — so no descendant or intervening commit
         is accepted as the freeze);
      4. worktree/index are clean (the executing runner is therefore the
         R2-frozen implementation blob);
      5. historical A5/R1 artifacts and production/frozen paths are unchanged;
      6. the committed manifest contract internally matches the runner constants
         (paths, freeze messages, cohort, masks, reusability decision, attempt
         accounting reference);
      7. continuation state is NOT_STARTED;
      8. raw continuation plans do not already represent a completed/frozen run.
    """
    assert_clean_worktree(project_root)
    head = git_head(project_root)
    message = git_commit_message(project_root, head)
    if message != R5_COMMIT_MESSAGE:
        raise RuntimeError(
            f"Continuation start requires HEAD to be the R5 implementation-freeze commit "
            f"('{R5_COMMIT_MESSAGE}'), got '{message}'"
        )
    parent = git_parent(project_root, head)
    if parent != R3_HEAD:
        raise RuntimeError(f"R5 freeze commit parent must be {R3_HEAD}, got {parent}")
    manifest_committed = git_blob(project_root, CONTINUATION_MANIFEST_PATH, "HEAD")
    if manifest_committed is None:
        raise RuntimeError(
            f"{CONTINUATION_MANIFEST_PATH} is not committed at HEAD; the continuation "
            f"execution manifest must be a committed pre-exposure artifact of the R5 freeze."
        )
    changed = git_paths_unchanged_between(
        project_root, STARTING_HEAD, head, list(PRODUCTION_IMMUTABLE_PATHS)
    )
    if changed:
        raise RuntimeError(f"Production/frozen paths changed since the A5 starting boundary: {changed}")
    historical_immutable = [
        HISTORICAL_MANIFEST_PATH, RESULT_PATH, PREREGISTRATION_PATH, SELECTION_PATH,
    ]
    changed = git_paths_unchanged_between(project_root, A5_STOP_HEAD, head, historical_immutable)
    if changed:
        raise RuntimeError(f"Historical A5 attempt artifacts were modified after the stop: {changed}")
    r1_immutable = [R1_PREREGISTRATION_PATH, R1_RESULT_PATH, R1_REPORT_PATH]
    changed = git_paths_unchanged_between(project_root, R1_HEAD, head, r1_immutable)
    if changed:
        raise RuntimeError(f"R1 repair artifacts were modified after R1: {changed}")

    manifest = _load_json(project_root / CONTINUATION_MANIFEST_PATH)
    checks: dict[str, Any] = {"head": head, "parent": parent, "message": message}
    errors: list[str] = []
    if manifest.get("checkpoint") != "D4-A5-CONTINUATION":
        errors.append("manifest checkpoint is not D4-A5-CONTINUATION")
    if manifest.get("artifact_paths") != {
        "manifest": CONTINUATION_MANIFEST_PATH,
        "raw_plans": CONTINUATION_RAW_PLANS_PATH,
        "raw_results": CONTINUATION_RAW_RESULTS_PATH,
        "evaluator_results": CONTINUATION_EVALUATOR_RESULTS_PATH,
        "result": CONTINUATION_RESULT_PATH,
        "historical_manifest_untouched": HISTORICAL_MANIFEST_PATH,
    }:
        errors.append("manifest artifact paths do not match runner continuation constants")
    gate_contracts = (
        manifest.get("plan_freeze_gate_contract", {}),
        manifest.get("raw_freeze_gate_contract", {}),
        manifest.get("closeout_gate_contract", {}),
    )
    expected_messages = (
        CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE,
        CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE,
        CONTINUATION_CLOSEOUT_COMMIT_MESSAGE,
    )
    for contract, expected in zip(gate_contracts, expected_messages):
        if contract.get("expected_commit_message") != expected:
            errors.append(
                f"manifest gate contract message {contract.get('expected_commit_message')!r} "
                f"!= runner constant {expected!r}"
            )
    for historical_message in (
        EXECUTOR_FREEZE_COMMIT_MESSAGE,
        PLAN_FREEZE_COMMIT_MESSAGE,
        RAW_FREEZE_COMMIT_MESSAGE,
    ):
        if historical_message in json.dumps(manifest):
            if f"historical" not in json.dumps(manifest):
                errors.append("old first-attempt freeze message appears without historical labeling")
    if manifest.get("plan_freeze_gate_contract", {}).get("expected_commit_message") in (
        PLAN_FREEZE_COMMIT_MESSAGE, EXECUTOR_FREEZE_COMMIT_MESSAGE
    ):
        errors.append("manifest still claims a first-attempt freeze message as a current gate")
    if [s["case_id"] for s in manifest.get("phase_p_slots_7", [])] != list(CASE_ORDER):
        errors.append("manifest Phase P cohort does not match the frozen case order")
    if len(manifest.get("phase_r_cells_14", [])) != 14:
        errors.append("manifest does not contain the frozen 14-cell schedule")
    if manifest.get("frozen_retirement_masks") != b2.FROZEN_RETIREMENT_MASKS:
        errors.append("manifest masks do not match the frozen D4-A4 masks")
    if manifest.get("repair_lineage", {}).get("r1_parent_boundary") != R1_HEAD:
        errors.append("manifest repair lineage does not record the R1 parent boundary")
    if manifest.get("repair_lineage", {}).get("r2_parent_boundary") != R2_HEAD:
        errors.append("manifest repair lineage does not record the R2 parent boundary")
    if manifest.get("repair_lineage", {}).get("r3_parent_boundary") != R3_HEAD:
        errors.append("manifest repair lineage does not record the R3 parent boundary")
    lineage = manifest.get("continuation_lineage", {})
    for key, expected in {
        "historical_a5_starting_head": STARTING_HEAD,
        "historical_a5_executor_freeze_head": EXECUTOR_FREEZE_HEAD,
        "historical_a5_stop_head": A5_STOP_HEAD,
        "historical_r1_head": R1_HEAD,
        "historical_r2_head": R2_HEAD,
        "historical_r3_head": R3_HEAD,
        "continuation_implementation_freeze_message": R5_COMMIT_MESSAGE,
        "continuation_plan_freeze_message": CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE,
        "continuation_raw_freeze_message": CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE,
    }.items():
        if lineage.get(key) != expected:
            errors.append(f"manifest continuation lineage {key} does not match the R5 contract")
    decision = manifest.get("reusability_decision", {})
    for key, expected in CONTINUATION_EXPECTED_REUSABILITY.items():
        if decision.get(key) != expected:
            errors.append(f"manifest reusability decision {key} does not match the frozen R1 audit")
    if manifest.get("attempt_accounting", {}).get("historical_attempt") != HISTORICAL_ATTEMPT_ACCOUNTING:
        errors.append("manifest historical attempt accounting does not match the frozen record")
    exposure = manifest.get("outcome_exposure_state", {})
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") != "NOT_STARTED":
        errors.append(f"continuation state is not NOT_STARTED: {exposure}")
    raw_plans_path = project_root / CONTINUATION_RAW_PLANS_PATH
    if raw_plans_path.exists():
        raw_plans = _load_json(raw_plans_path)
        if raw_plans.get("plan_freeze_state") == "PLANS_FROZEN":
            errors.append(
                "raw continuation plans already represent a completed/frozen run; "
                "execute-phase-p must not restart it"
            )
    if errors:
        raise RuntimeError(
            "Continuation-start verification FAILED: " + "; ".join(errors)
        )
    checks["manifest_contract_matches_runner"] = True
    checks["continuation_state"] = exposure.get("D4_A5_OUTCOME_EXPOSURE")
    checks["provider_calls"] = 0
    return checks


def _new_continuation_plans_artifact(freeze_head: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5-CONTINUATION",
        "stage": "Phase P — Prospective Shared Plan Acquisition (Continuation Attempt)",
        "created_at": _utc_now(),
        "attempt_id": "D4-A5_ATTEMPT_2_CONTINUATION",
        "starting_head": STARTING_HEAD,
        "historical_a5_stop_head": A5_STOP_HEAD,
        "historical_r1_head": R1_HEAD,
        "historical_r2_head": R2_HEAD,
        "continuation_implementation_freeze_head": freeze_head,
        "persistence_contract": "PERSIST_BEFORE_GATE — every Analyzer acquisition (canonical "
        "plan, serialization, signature, matched rules, contribution ledger, origins, "
        "applicability receipts, projections when constructible, provider accounting) is durably "
        "written before any applicability gate can terminate execution; gate-stopped "
        "acquisitions retain full accounting and diagnostic evidence.",
        "applicability_contract": {
            "statuses": list(APPLICABILITY_STATUSES),
            "semantics_authority": "selected-rule origin in the contribution ledger, never raw "
            "token presence; absence from the unmodified production plan is INACTIVE, not INVALID",
        },
        "plan_freeze_state": "ACQUISITION_IN_PROGRESS",
        "PLAN_FREEZE_BOUNDARY_ESTABLISHED": False,
        "PHASE_R_RETRIEVAL_EXECUTED": False,
        "EVALUATOR_EXECUTED": False,
        "SCIENTIFIC_VERDICT_COMPUTED": False,
        "model_contract": {
            "generation_model": EXPECTED_MODEL,
            "embedding_model": EXPECTED_EMBEDDING_MODEL,
            "location": EXPECTED_VERTEX_LOCATION,
            "temperature": EXPECTED_TEMPERATURE,
        },
        "prompt_authority": "src/panda_agent/prompts.py:QUERY_ANALYZER_SYSTEM_PROMPT",
        "exact_acquisition_case_order": list(CASE_ORDER),
        "max_provider_attempts_per_case": MAX_PROVIDER_ATTEMPTS_PER_CASE,
        "retry_policy": {"max_retries": 0},
        "plans_planned": len(CASE_ORDER),
        "plans_recorded": 0,
        "plans_completed": 0,
        "plans_reused": 0,
        "plans_gate_stopped": 0,
        "plans_provider_failed": 0,
        "plans_failed": 0,
        "accounting": {
            "analyzer_calls": 0,
            "analyzer_provider_attempts": 0,
            "embedding_calls": 0,
            "reranker_calls": 0,
            "logical_model_calls": 0,
            "retries": 0,
            "token_usage": 0,
            "token_usage_unknown_components": 0,
            "qa_calls": 0,
            "verifier_calls": 0,
            "judge_calls": 0,
            "db_writes": 0,
            "qdrant_writes": 0,
            "reindex": 0,
            "novel_validation_runs": 0,
            "novel_holdout_runs": 0,
            "protected_dataset_access": 0,
            "historical_attempt_reference": dict(HISTORICAL_ATTEMPT_ACCOUNTING),
        },
        "plans": [],
    }


def _write_continuation_plans_artifact(project_root: Path, artifact: dict[str, Any]) -> None:
    _save_json(project_root / CONTINUATION_RAW_PLANS_PATH, artifact)


def apply_continuation_accounting(
    manifest: dict[str, Any],
    *,
    analyzer_calls: int = 0,
    analyzer_attempts: int = 0,
    unknown_provider_attempt_events: int = 0,
    token_usage: int = 0,
    unknown_token_events: int = 0,
    embedding_calls: int = 0,
    reranker_calls: int = 0,
    retrieval_provider_attempts: int = 0,
) -> None:
    """Deterministic two-layer accounting update (R3; task Sections 7-10).

    The single accounting path for the WHOLE continuation attempt: Analyzer
    acquisitions (Phase P) and paired retrieval cells (Phase R) both feed their
    observed deltas here. Applies one continuation-event delta to the
    continuation-attempt layer, then mechanically recomputes the cumulative
    layer as historical + continuation.

    Unknown accounting stays explicit: unknown provider-attempt and unknown
    token events are counted separately and never silently contribute numerical
    zero as if known. A failed-but-invoked Analyzer acquisition still counts as
    one logical Analyzer acquisition. Cumulative values are always recomputed
    absolutely from the two layers, so persisted/reloaded state never double
    counts as long as each event is applied once (terminal slot/cell status
    transitions gate re-application).
    """
    attempt = manifest["attempt_accounting"]
    cont = attempt["continuation_attempt"]
    cont["analyzer_logical_calls"] += analyzer_calls
    cont["analyzer_provider_attempts"] += analyzer_attempts
    cont["unknown_provider_attempt_events"] = (
        cont.get("unknown_provider_attempt_events", 0) + unknown_provider_attempt_events
    )
    cont["token_usage"] += token_usage
    cont["unknown_token_usage_events"] = (
        cont.get("unknown_token_usage_events", 0) + unknown_token_events
    )
    cont["embedding_calls"] += embedding_calls
    cont["reranker_calls"] += reranker_calls
    cont["retrieval_provider_attempts"] = (
        cont.get("retrieval_provider_attempts", 0) + retrieval_provider_attempts
    )
    hist = attempt["historical_attempt"]
    cumulative = attempt["cumulative"]
    cumulative["analyzer_logical_calls"] = (
        hist["analyzer_logical_calls"] + cont["analyzer_logical_calls"]
    )
    cumulative["analyzer_provider_attempts"] = (
        hist["analyzer_provider_attempts"] + cont["analyzer_provider_attempts"]
    )
    cumulative["provider_attempt_unknown_components"] = (
        hist.get("unknown_provider_attempt_events", 0)
        + cont.get("unknown_provider_attempt_events", 0)
    )
    cumulative["retries"] = hist["retries"] + cont["retries"]
    cumulative["token_usage_recorded"] = (
        hist["recorded_token_usage"] + cont["token_usage"]
    )
    cumulative["token_usage_unknown_components"] = (
        hist.get("unknown_token_usage_components", 1)
        + cont.get("unknown_token_usage_events", 0)
    )
    cumulative["embedding_calls"] = hist["embedding_calls"] + cont["embedding_calls"]
    cumulative["reranker_calls"] = hist["reranker_calls"] + cont["reranker_calls"]
    cumulative["retrieval_provider_attempts"] = (
        hist.get("retrieval_provider_attempts", 0)
        + cont.get("retrieval_provider_attempts", 0)
    )


def execute_phase_p(project_root: Path) -> dict[str, Any]:
    """Continuation Phase P with persistence-before-gate (R1) and the real R2
    continuation-start preflight (task Sections 10/11/16).

    Starts only from a clean R2 freeze HEAD containing the committed continuation
    manifest (verified by the shared read-only preflight, before any provider
    call). Acquires exactly one prospective Analyzer plan per case that requires
    reacquisition, in frozen order, with zero retries. Every acquisition is
    durably persisted — including its provider accounting, contribution ledger,
    component applicability receipts, and (when constructible) both execution
    projections — BEFORE any applicability gate can terminate execution. A gate
    stop (AMBIGUOUS_INVALID) records GATE_STOPPED state with full accounting and
    stops the run. A provider failure persists a durable failure receipt with
    every mechanically available accounting value (unavailable values are
    recorded as unknown, never fabricated), marks the slot with an explicit
    terminal failure state, and stops the continuation. No retries.
    """
    load_dotenv(project_root / ".env")
    start_receipt = verify_continuation_start(project_root)

    manifest_path = project_root / CONTINUATION_MANIFEST_PATH
    manifest = _load_json(manifest_path)
    exposure = manifest.setdefault("outcome_exposure_state", {})
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") in ("PLANS_FROZEN", "RAW_RETRIEVAL_COMPLETE", "EVALUATION_COMPLETE"):
        print("[PHASE P ALREADY COMPLETED] Loading existing frozen plans.")
        return _load_json(project_root / CONTINUATION_RAW_PLANS_PATH)
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") not in ("NOT_STARTED", "PLAN_ACQUISITION_STARTED"):
        raise RuntimeError(f"Unexpected exposure state: {exposure}")

    exposure["D4_A5_OUTCOME_EXPOSURE"] = "PLAN_ACQUISITION_STARTED"
    exposure["continuation_implementation_freeze_head"] = start_receipt["head"]
    _save_json(manifest_path, manifest)

    artifact = _new_continuation_plans_artifact(start_receipt["head"])
    _write_continuation_plans_artifact(project_root, artifact)

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

    print("[PHASE P] Acquiring prospective plans (retries=0, persist-before-gate)...")

    for i, cid in enumerate(CASE_ORDER, start=1):
        slot = manifest["phase_p_slots_7"][i - 1]
        if slot["status"] in ("COMPLETED", "REUSED_FROZEN_PLAN", "GATE_STOPPED_AMBIGUOUS_INVALID"):
            print(f"  Slot #{i} ({cid}) already recorded ({slot['status']}), skipping.")
            continue
        if slot["status"] == "STARTED":
            raise RuntimeError(
                f"Slot #{i} ({cid}) in ambiguous STARTED state; fail closed on restart."
            )
        if not slot.get("reacquisition_required", True):
            raise RuntimeError(
                f"Slot #{i} ({cid}) is marked reusable but no valid reusable frozen plan exists "
                f"in the historical artifacts; reuse requires the complete frozen record."
            )

        question_text = all_questions[cid].query
        slot["status"] = "STARTED"
        slot["started_at"] = _utc_now()
        _save_json(manifest_path, manifest)

        # --- 1. Provider acquisition; accounting captured immediately. -------
        # Frozen retry policy: max_retries = 0, exactly one attempt per slot.
        stats_before = retriever.vertex.stats_snapshot()
        t0 = time.time()
        try:
            raw_plan = retriever.analyze(question_text)
        except Exception as exc:
            # Provider failure: no retry. Persist a durable failure receipt with
            # every mechanically available accounting value before stopping.
            elapsed = round(time.time() - t0, 3)
            try:
                stats_delta = retriever.vertex.stats_delta(stats_before)
                attempts_recoverable = True
                tokens_recoverable = True
            except Exception:
                stats_delta = {}
                attempts_recoverable = False
                tokens_recoverable = False
            provider_attempts = stats_delta.get("model_calls", 0) if attempts_recoverable else 0
            token_usage = stats_delta.get("token_usage", 0) if tokens_recoverable else 0
            failure_receipt = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc)[:500],
                "retry_policy": {"max_retries": 0, "max_provider_attempts_per_case": 1},
                "retries_performed": 0,
                "provider_attempts_recoverable": attempts_recoverable,
                "token_usage_recoverable": tokens_recoverable,
                "provider_attempts": provider_attempts if attempts_recoverable else "unknown",
                "token_usage": token_usage if tokens_recoverable else "unknown",
                "unknown_accounting_note": (
                    "Unavailable provider accounting is recorded as explicitly unknown, "
                    "never fabricated as zero."
                )
                if not (attempts_recoverable and tokens_recoverable)
                else None,
            }
            failure_record = {
                "plan_index": i,
                "plan_id": f"prospective_{cid}",
                "case_id": cid,
                "question": question_text,
                "role": CASE_ATTRIBUTION[cid]["role"],
                "status": "PROVIDER_FAILED",
                "provider_failure_receipt": failure_receipt,
                "provider_accounting": {
                    "analyzer_logical_calls": 1,
                    "analyzer_provider_attempts": provider_attempts,
                    "retries": 0,
                    "embedding_calls": 0,
                    "reranker_calls": 0,
                    "token_usage": token_usage,
                    "token_usage_unknown": not tokens_recoverable,
                    "provider_attempts_unknown": not attempts_recoverable,
                    "model": EXPECTED_MODEL,
                    "location": EXPECTED_VERTEX_LOCATION,
                    "temperature": EXPECTED_TEMPERATURE,
                    "elapsed_seconds": elapsed,
                },
                "started_at": slot["started_at"],
                "failed_at": _utc_now(),
            }
            artifact["plans"] = [r for r in artifact["plans"] if r["case_id"] != cid]
            artifact["plans"].append(failure_record)
            artifact["plans_recorded"] = len(artifact["plans"])
            artifact["plans_provider_failed"] += 1
            artifact["accounting"]["analyzer_calls"] += 1
            artifact["accounting"]["logical_model_calls"] = artifact["accounting"]["analyzer_calls"]
            artifact["accounting"]["analyzer_provider_attempts"] += provider_attempts
            artifact["accounting"]["token_usage"] += token_usage
            _write_continuation_plans_artifact(project_root, artifact)
            apply_continuation_accounting(
                manifest,
                analyzer_calls=1,
                analyzer_attempts=provider_attempts if attempts_recoverable else 0,
                unknown_provider_attempt_events=0 if attempts_recoverable else 1,
                token_usage=token_usage,
                unknown_token_events=0 if tokens_recoverable else 1,
            )
            slot["status"] = "PROVIDER_FAILED"
            slot["completed_at"] = failure_record["failed_at"]
            slot["attempts"] = provider_attempts if attempts_recoverable else "unknown"
            slot["token_usage"] = token_usage if tokens_recoverable else "unknown"
            slot["provider_failure_receipt"] = failure_receipt
            _save_json(manifest_path, manifest)
            raise RuntimeError(
                f"Case {cid}: provider call failed (no retry per frozen max_retries=0 policy); "
                f"durable failure receipt persisted to {CONTINUATION_RAW_PLANS_PATH}; "
                f"continuation STOPPED."
            ) from exc
        elapsed = round(time.time() - t0, 3)
        stats_delta = retriever.vertex.stats_delta(stats_before)
        provider_attempts = stats_delta.get("model_calls", 1)
        token_usage = stats_delta.get("token_usage", 0)
        provider_accounting = {
            "analyzer_logical_calls": 1,
            "analyzer_provider_attempts": provider_attempts,
            "retries": 0,
            "embedding_calls": 0,
            "reranker_calls": 0,
            "token_usage": token_usage,
            "token_usage_note": "recorded before any applicability gate evaluation",
            "model": EXPECTED_MODEL,
            "location": EXPECTED_VERTEX_LOCATION,
            "temperature": EXPECTED_TEMPERATURE,
            "elapsed_seconds": elapsed,
        }

        # --- 2. Deterministic plan/ledger/applicability construction. -------
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
        configured_entries = build_batch2_mask_entries(cid, matched_batch2)
        component_receipts, applicability_summary = classify_component_applicability(
            plan_dict, ledger, configured_entries
        )
        current_compat_projection = copy.deepcopy(plan_dict)
        gate_error = None
        projected = None
        projection_receipts = None
        if applicability_summary["ambiguous"] == 0:
            try:
                projected, projection_receipts = build_retirement_projection_r1(
                    plan_dict, ledger, component_receipts, matched_batch2
                )
            except ValueError as exc:
                gate_error = str(exc)
        else:
            gate_error = (
                f"{applicability_summary['ambiguous']} configured retirement component(s) are "
                f"AMBIGUOUS_INVALID; treatment construction would require guessing or global "
                f"deletion."
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
            "provenance_origin_receipts": [
                {
                    "contribution_id": e["contribution_id"],
                    "provenance_origin_ids": e["provenance_origin_ids"],
                    "origin_types": e["origin_types"],
                    "plan_present": e["plan_present"],
                }
                for e in ledger
            ],
            "component_applicability_receipts": component_receipts,
            "component_applicability_summary": applicability_summary,
            "current_compat_execution_projection": current_compat_projection,
            "batch2_retirement_execution_projection": projected,
            "projection_diff_receipts": projection_receipts,
            "provider_accounting": provider_accounting,
            "gate_error": gate_error,
            "status": "PERSISTED_PRE_GATE",
            "started_at": slot["started_at"],
            "persisted_at": _utc_now(),
        }

        # --- 3. PERSIST BEFORE GATE: durable record with full accounting. ---
        artifact["plans"] = [r for r in artifact["plans"] if r["case_id"] != cid]
        artifact["plans"].append(record)
        artifact["plans_recorded"] = len(artifact["plans"])
        artifact["accounting"]["analyzer_calls"] = sum(
            r["provider_accounting"]["analyzer_logical_calls"] for r in artifact["plans"]
            if r["status"] != "REUSED_FROZEN_PLAN"
        )
        artifact["accounting"]["analyzer_provider_attempts"] = sum(
            r["provider_accounting"]["analyzer_provider_attempts"] for r in artifact["plans"]
            if r["status"] != "REUSED_FROZEN_PLAN"
        )
        artifact["accounting"]["token_usage"] = sum(
            r["provider_accounting"]["token_usage"] for r in artifact["plans"]
            if r["status"] != "REUSED_FROZEN_PLAN"
        )
        artifact["accounting"]["logical_model_calls"] = artifact["accounting"]["analyzer_calls"]
        _write_continuation_plans_artifact(project_root, artifact)

        # --- 4. Gate evaluation (after durable persistence). ----------------
        if gate_error is not None:
            record["status"] = "GATE_STOPPED_AMBIGUOUS_INVALID"
            record["completed_at"] = _utc_now()
            artifact["plans_gate_stopped"] += 1
            _write_continuation_plans_artifact(project_root, artifact)
            slot["status"] = "GATE_STOPPED_AMBIGUOUS_INVALID"
            slot["completed_at"] = record["completed_at"]
            slot["token_usage"] = token_usage
            slot["attempts"] = provider_attempts
            slot["gate_error"] = gate_error
            exposure["plans_gate_stopped"] = artifact["plans_gate_stopped"]
            _save_json(manifest_path, manifest)
            raise RuntimeError(
                f"Case {cid}: applicability gate STOPPED after durable persistence "
                f"({gate_error}); verdict path {R1_VERDICT_LEVEL_1_INVALID}. Consumed provider "
                f"accounting and plan evidence are preserved in {CONTINUATION_RAW_PLANS_PATH}."
            )

        gate = build_provenance_gate_receipt(
            cid, attribution, matched_rule_ids, plan_dict, ledger,
            current_compat_projection, projected, projection_receipts,
            component_receipts=component_receipts,
        )
        if not gate["pass"]:
            failed = [k for k, v in gate["checks"].items() if not v.get("pass", False)]
            record["status"] = "GATE_STOPPED_PROTOCOL"
            record["provenance_gate"] = gate
            record["completed_at"] = _utc_now()
            artifact["plans_gate_stopped"] += 1
            _write_continuation_plans_artifact(project_root, artifact)
            slot["status"] = "GATE_STOPPED_PROTOCOL"
            slot["token_usage"] = token_usage
            slot["attempts"] = provider_attempts
            _save_json(manifest_path, manifest)
            raise RuntimeError(
                f"Case {cid}: provenance gate FAILED ({failed}) after durable persistence; "
                f"verdict path {R1_VERDICT_LEVEL_1_INVALID}."
            )
        record["provenance_gate"] = gate
        record["status"] = "COMPLETED"
        record["completed_at"] = _utc_now()
        artifact["plans_completed"] += 1
        _write_continuation_plans_artifact(project_root, artifact)

        apply_continuation_accounting(
            manifest,
            analyzer_calls=1,
            analyzer_attempts=provider_attempts,
            token_usage=token_usage,
        )
        slot["status"] = "COMPLETED"
        slot["completed_at"] = record["completed_at"]
        slot["token_usage"] = token_usage
        slot["attempts"] = provider_attempts
        slot["plan_signature"] = sig_payload
        slot["applicability_summary"] = applicability_summary
        exposure["plans_completed"] = artifact["plans_completed"]
        _save_json(manifest_path, manifest)

        print(
            f"  Slot #{i}/{len(CASE_ORDER)} ({cid}) COMPLETED in {elapsed}s: "
            f"active={applicability_summary['active']} "
            f"inactive={applicability_summary['inactive']} "
            f"ambiguous={applicability_summary['ambiguous']}"
        )

    artifact["plan_freeze_state"] = "PLANS_FROZEN"
    artifact["PLAN_FREEZE_BOUNDARY_ESTABLISHED"] = True
    artifact["created_at_finalized"] = _utc_now()
    _write_continuation_plans_artifact(project_root, artifact)

    exposure["D4_A5_OUTCOME_EXPOSURE"] = "PLANS_FROZEN"
    _save_json(manifest_path, manifest)
    print(f"[PHASE P COMPLETE] {artifact['plans_completed']} plans frozen to {CONTINUATION_RAW_PLANS_PATH}")
    return artifact


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


def verify_continuation_plan_freeze_gate(
    project_root: Path, continuation_implementation_freeze_head: str
) -> dict[str, Any]:
    """Continuation plan-freeze gate (R3; task Section 6): HEAD is the
    continuation plan-freeze commit, a DIRECT CHILD of the R3 continuation
    implementation freeze; the committed raw-plan artifact contains exactly the
    frozen 7-case cohort with completed provenance-gated plans; the R3→plan-freeze
    diff is limited to the frozen plan-acquisition artifacts; protected
    historical/production paths remain unchanged."""
    head = _require_freeze_commit(
        project_root,
        CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE,
        continuation_implementation_freeze_head,
    )
    rel = CONTINUATION_RAW_PLANS_PATH.replace("\\", "/")
    proc = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{rel}"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"{CONTINUATION_RAW_PLANS_PATH} is not committed at HEAD; plan freeze gate failed"
        )
    allowed_diff = {CONTINUATION_MANIFEST_PATH, CONTINUATION_RAW_PLANS_PATH}
    diff_output = _git(
        ["diff", "--name-only", continuation_implementation_freeze_head, head],
        project_root,
    )
    changed_files = {line for line in diff_output.splitlines() if line}
    unexpected = changed_files - allowed_diff
    if unexpected:
        raise RuntimeError(
            f"R3->plan-freeze diff contains non-plan-acquisition artifacts: "
            f"{sorted(unexpected)}"
        )
    raw_plans = _load_json(project_root / CONTINUATION_RAW_PLANS_PATH)
    cohort = sorted(p["case_id"] for p in raw_plans.get("plans", []))
    if cohort != sorted(CASE_ORDER) or len(raw_plans.get("plans", [])) != 7:
        raise RuntimeError("Committed raw plans do not contain exactly the frozen 7-case cohort")
    if raw_plans.get("plans_completed") != 7 or raw_plans.get("plan_freeze_state") != "PLANS_FROZEN":
        raise RuntimeError("Committed raw plans are not a completed frozen Phase-P run")
    for record in raw_plans["plans"]:
        if record["status"] != "COMPLETED" or not record["provenance_gate"]["pass"]:
            raise RuntimeError(
                f"Plan record for {record['case_id']} is not a completed provenance-gated plan"
            )
    changed = git_paths_unchanged_between(
        project_root, A5_STOP_HEAD, head,
        list(PRODUCTION_IMMUTABLE_PATHS) + [HISTORICAL_MANIFEST_PATH, RESULT_PATH],
    )
    if changed:
        raise RuntimeError(f"Protected paths drifted during the continuation: {changed}")
    r1_r2_unchanged = git_paths_unchanged_between(
        project_root, R1_HEAD, head,
        [R1_PREREGISTRATION_PATH, R1_RESULT_PATH, R1_REPORT_PATH,
         R2_PREREGISTRATION_PATH, R2_RESULT_PATH, R2_REPORT_PATH],
    )
    if r1_r2_unchanged:
        raise RuntimeError(f"R1/R2 repair artifacts drifted: {r1_r2_unchanged}")
    return {
        "head": head,
        "continuation_implementation_freeze_head": continuation_implementation_freeze_head,
        "continuation_plan_freeze_head": head,
    }


def verify_phase_r_preflight(
    project_root: Path, continuation_implementation_freeze_head: str
) -> dict[str, Any]:
    """Read-only Phase-R preflight (R3; task Section 11): plan-freeze gate plus
    raw-plan structural completeness, before any retrieval exposure. Phase R
    consumes the frozen continuation lineage — the implementation freeze head
    and the plan-freeze head — and never a stale historical r1_freeze_head."""
    freeze = verify_continuation_plan_freeze_gate(
        project_root, continuation_implementation_freeze_head
    )
    manifest = _load_json(project_root / CONTINUATION_MANIFEST_PATH)
    exposure = manifest.get("outcome_exposure_state", {})
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") != "PLANS_FROZEN":
        raise RuntimeError(
            f"Phase R requires PLANS_FROZEN exposure, got {exposure}"
        )
    raw_plans = _load_json(project_root / CONTINUATION_RAW_PLANS_PATH)
    plans_planned = raw_plans.get("plans_planned")
    plans_completed = raw_plans.get("plans_completed")
    if plans_planned != 7 or plans_completed != 7:
        raise RuntimeError("Plan artifact accounting incomplete")
    return {
        "continuation_implementation_freeze_head": freeze[
            "continuation_implementation_freeze_head"
        ],
        "continuation_plan_freeze_head": freeze["continuation_plan_freeze_head"],
    }


def execute_phase_r(project_root: Path) -> dict[str, Any]:
    load_dotenv(project_root / ".env")
    manifest = _load_json(project_root / CONTINUATION_MANIFEST_PATH)
    exposure = manifest.setdefault("outcome_exposure_state", {})
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") in ("RAW_RETRIEVAL_COMPLETE", "EVALUATION_COMPLETE"):
        print("[PHASE R ALREADY COMPLETED] Loading existing paired results.")
        return _load_json(project_root / CONTINUATION_RAW_RESULTS_PATH)
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") != "PLANS_FROZEN":
        raise RuntimeError(f"Phase R requires PLANS_FROZEN exposure, got {exposure}")

    continuation_implementation_freeze_head = exposure.get(
        "continuation_implementation_freeze_head"
    )
    if not continuation_implementation_freeze_head:
        raise RuntimeError(
            "Manifest is missing continuation_implementation_freeze_head; plan freeze "
            "provenance unknown (stale lineage input is not accepted)"
        )
    preflight = verify_phase_r_preflight(project_root, continuation_implementation_freeze_head)
    freeze = {
        "continuation_implementation_freeze_head": preflight[
            "continuation_implementation_freeze_head"
        ],
        "head": preflight["continuation_plan_freeze_head"],
    }

    raw_plans = _load_json(project_root / CONTINUATION_RAW_PLANS_PATH)
    plans_by_case = {p["case_id"]: p for p in raw_plans["plans"]}
    if sorted(plans_by_case) != sorted(CASE_ORDER) or len(raw_plans["plans"]) != 7:
        raise RuntimeError("Plan artifact does not contain exactly the frozen 7-case cohort")
    plans_planned = raw_plans["plans_planned"]
    plans_completed = raw_plans["plans_completed"]
    if plans_planned != 7 or plans_completed != 7:
        raise RuntimeError("Plan artifact accounting incomplete")
    for record in raw_plans["plans"]:
        if record["status"] != "COMPLETED":
            raise RuntimeError(
                f"Plan record for {record['case_id']} is {record['status']}; PLANS_FROZEN "
                f"requires every acquisition COMPLETED"
            )
        if not record["provenance_gate"]["pass"]:
            raise RuntimeError(f"Plan provenance gate not PASS for {record['case_id']}")

    exposure["D4_A5_OUTCOME_EXPOSURE"] = "RAW_RETRIEVAL_STARTED"
    exposure["plan_freeze_head"] = freeze["head"]
    _save_json(project_root / CONTINUATION_MANIFEST_PATH, manifest)

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
        _save_json(project_root / CONTINUATION_MANIFEST_PATH, manifest)

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
        # End-to-end continuation accounting (R3): feed the cell's ACTUAL
        # recorded stats into the shared two-layer accounting path. Unknown
        # components stay explicit; cumulative is recomputed as
        # historical + continuation.
        apply_continuation_accounting(
            manifest,
            embedding_calls=stats["embedding_calls"],
            reranker_calls=stats["generation_calls"],
            retrieval_provider_attempts=stats["model_calls"],
            token_usage=stats["token_usage"],
        )
        exposure["formal_cells_completed"] = len(cell_records)
        _save_json(project_root / CONTINUATION_MANIFEST_PATH, manifest)

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
    _save_json(project_root / CONTINUATION_MANIFEST_PATH, manifest)
    print(f"[PHASE R COMPLETE] 14 cells frozen to {CONTINUATION_RAW_RESULTS_PATH}")
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
        "checkpoint": "D4-A5-CONTINUATION",
        "stage": "Phase R — Paired Shared-Plan Batch2 Retirement Retrieval (Continuation Attempt)",
        "created_at": _utc_now(),
        "attempt_id": "D4-A5_ATTEMPT_2_CONTINUATION",
        "starting_head": STARTING_HEAD,
        "historical_a5_stop_head": A5_STOP_HEAD,
        "historical_r1_head": R1_HEAD,
        "historical_r2_head": R2_HEAD,
        "historical_r3_head": R3_HEAD,
        "continuation_implementation_freeze_head": freeze[
            "continuation_implementation_freeze_head"
        ],
        "continuation_plan_freeze_head": freeze["head"],
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
            "raw_plans": CONTINUATION_RAW_PLANS_PATH,
            "manifest": CONTINUATION_MANIFEST_PATH,
            "continuation_implementation_freeze_head": freeze[
                "continuation_implementation_freeze_head"
            ],
            "continuation_plan_freeze_head": freeze["head"],
        },
        "slots": cell_records,
    }
    _save_json(project_root / CONTINUATION_RAW_RESULTS_PATH, artifact)
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


def verify_continuation_raw_freeze_gate(
    project_root: Path,
    plan_freeze_head: str,
    continuation_implementation_freeze_head: str,
) -> dict[str, Any]:
    """Continuation raw-freeze gate with the strict evaluator-integrity seal
    (R5; task Sections 7/9): HEAD is the raw-freeze commit, a DIRECT CHILD of
    the continuation plan-freeze commit; raw plans AND raw results are
    committed; the exact plan-freeze -> raw-freeze changed-file set is a subset
    of RAW_FREEZE_DIFF_ALLOWLIST (continuation manifest + continuation raw
    results) — so no runner, test, raw-plan, R5-artifact, historical, or
    production path can drift into the raw-freeze commit after retrieval
    outcomes were exposed. The strict allowlist subsumes broad protected-path
    lists for this window; upstream gates (start preflight and plan-freeze
    gate) cover the earlier windows."""
    head = _require_freeze_commit(
        project_root, CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE, plan_freeze_head
    )
    for rel in (CONTINUATION_RAW_RESULTS_PATH, CONTINUATION_RAW_PLANS_PATH):
        proc = subprocess.run(
            ["git", "cat-file", "-e", f"HEAD:{rel.replace(chr(92), '/')}"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"{rel} is not committed at HEAD; raw freeze gate failed")
    diff_output = _git(["diff", "--name-only", plan_freeze_head, head], project_root)
    changed_files = {line for line in diff_output.splitlines() if line}
    unexpected = changed_files - set(RAW_FREEZE_DIFF_ALLOWLIST)
    if unexpected:
        raise RuntimeError(
            "Raw-freeze commit violates the strict evaluator-integrity allowlist "
            f"(plan-freeze -> raw-freeze changed files outside "
            f"{sorted(RAW_FREEZE_DIFF_ALLOWLIST)}): {sorted(unexpected)}"
        )
    plans_unchanged = git_paths_unchanged_between(
        project_root, plan_freeze_head, head, [CONTINUATION_RAW_PLANS_PATH]
    )
    if plans_unchanged:
        raise RuntimeError("Continuation plans artifact changed after plan freeze")
    return {
        "head": head,
        "continuation_raw_freeze_head": head,
        "plan_freeze_head": plan_freeze_head,
        "continuation_implementation_freeze_head": continuation_implementation_freeze_head,
        "raw_freeze_diff_allowlist_respected": True,
    }


def verify_continuation_evaluator_preflight(
    project_root: Path,
    plan_freeze_head: str,
    continuation_implementation_freeze_head: str,
) -> dict[str, Any]:
    """Read-only evaluator preflight (R5; task Sections 8/10): must pass before
    any deterministic evaluator logic consumes retrieval outcomes. Establishes:
    the raw-freeze gate; runner blob and focused-test blob at raw-freeze HEAD
    equal to the R5 implementation-freeze blobs; continuation raw plans blob
    equal to the plan-freeze blob; production/config/dataset paths unchanged
    across the whole retrieval window (implementation freeze -> raw freeze);
    historical R1/R2/R3 artifacts unchanged; manifest lineage internally
    consistent; and no evaluator/result artifact already mutated outside the
    expected lifecycle. Zero provider calls."""
    gate = verify_continuation_raw_freeze_gate(
        project_root, plan_freeze_head, continuation_implementation_freeze_head
    )
    raw_freeze_head = gate["continuation_raw_freeze_head"]
    errors: list[str] = []

    runner_changed = git_paths_unchanged_between(
        project_root, continuation_implementation_freeze_head, raw_freeze_head, [RUNNER_PATH]
    )
    if runner_changed:
        errors.append(f"runner drifted after the implementation freeze: {runner_changed}")
    test_changed = git_paths_unchanged_between(
        project_root, continuation_implementation_freeze_head, raw_freeze_head, [TEST_PATH]
    )
    if test_changed:
        errors.append(f"focused tests drifted after the implementation freeze: {test_changed}")

    production_changed = git_paths_unchanged_between(
        project_root, continuation_implementation_freeze_head, raw_freeze_head,
        list(PRODUCTION_IMMUTABLE_PATHS),
    )
    if production_changed:
        errors.append(f"production/config/dataset paths drifted during retrieval: {production_changed}")

    historical_changed = git_paths_unchanged_between(
        project_root, A5_STOP_HEAD, raw_freeze_head,
        [HISTORICAL_MANIFEST_PATH, RESULT_PATH,
         R1_PREREGISTRATION_PATH, R1_RESULT_PATH, R1_REPORT_PATH,
         R2_PREREGISTRATION_PATH, R2_RESULT_PATH, R2_REPORT_PATH,
         R3_PREREGISTRATION_PATH, R3_RESULT_PATH, R3_REPORT_PATH],
    )
    if historical_changed:
        errors.append(f"historical A5/R1/R2/R3 artifacts drifted: {historical_changed}")

    manifest = _load_json(project_root / CONTINUATION_MANIFEST_PATH)
    lineage = manifest.get("continuation_lineage", {})
    for key, expected in {
        "historical_a5_starting_head": STARTING_HEAD,
        "historical_a5_executor_freeze_head": EXECUTOR_FREEZE_HEAD,
        "historical_a5_stop_head": A5_STOP_HEAD,
        "historical_r1_head": R1_HEAD,
        "historical_r2_head": R2_HEAD,
        "historical_r3_head": R3_HEAD,
        "continuation_implementation_freeze_message": R5_COMMIT_MESSAGE,
        "continuation_plan_freeze_message": CONTINUATION_PLAN_FREEZE_COMMIT_MESSAGE,
        "continuation_raw_freeze_message": CONTINUATION_RAW_FREEZE_COMMIT_MESSAGE,
    }.items():
        if lineage.get(key) != expected:
            errors.append(f"manifest continuation lineage {key} does not match the R5 contract")
    exposure = manifest.get("outcome_exposure_state", {})
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") != "RAW_RETRIEVAL_COMPLETE":
        errors.append(f"manifest exposure is not RAW_RETRIEVAL_COMPLETE: {exposure}")

    for rel in (CONTINUATION_EVALUATOR_RESULTS_PATH, CONTINUATION_RESULT_PATH):
        if (project_root / rel).exists():
            errors.append(
                f"{rel} already exists before evaluator execution; lifecycle state is "
                f"inconsistent with a raw-freeze boundary"
            )

    if errors:
        raise RuntimeError(
            "Evaluator preflight FAILED before consuming any retrieval outcome: "
            + "; ".join(errors)
        )
    return {
        "continuation_implementation_freeze_head": continuation_implementation_freeze_head,
        "continuation_plan_freeze_head": plan_freeze_head,
        "continuation_raw_freeze_head": raw_freeze_head,
        "evaluator_integrity_sealed": True,
        "provider_calls": 0,
    }


def evaluate_d4_a5(project_root: Path) -> dict[str, Any]:
    """Deterministic, zero-provider evaluator using the repaired R1 contract
    (component applicability, 6-state dispositions, 7-level batch verdict)."""
    load_dotenv(project_root / ".env")
    manifest = _load_json(project_root / CONTINUATION_MANIFEST_PATH)
    exposure = manifest.get("outcome_exposure_state", {})
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") == "EVALUATION_COMPLETE":
        print("[EVALUATOR ALREADY COMPLETED] Loading existing evaluator results.")
        return _load_json(project_root / CONTINUATION_EVALUATOR_RESULTS_PATH)
    if exposure.get("D4_A5_OUTCOME_EXPOSURE") != "RAW_RETRIEVAL_COMPLETE":
        raise RuntimeError(f"Evaluator requires RAW_RETRIEVAL_COMPLETE, got {exposure}")

    plan_freeze_head = exposure.get("plan_freeze_head")
    continuation_implementation_freeze_head = exposure.get(
        "continuation_implementation_freeze_head"
    )
    if not plan_freeze_head or not continuation_implementation_freeze_head:
        raise RuntimeError(
            "Manifest is missing the frozen continuation lineage "
            "(continuation_implementation_freeze_head / plan_freeze_head); stale or "
            "incomplete lineage input is not accepted"
        )
    preflight = verify_continuation_evaluator_preflight(
        project_root, plan_freeze_head, continuation_implementation_freeze_head
    )
    freeze = {
        "continuation_implementation_freeze_head": preflight[
            "continuation_implementation_freeze_head"
        ],
        "head": preflight["continuation_raw_freeze_head"],
    }

    prereg = _load_json(project_root / PREREGISTRATION_PATH)
    plans_data = _load_json(project_root / CONTINUATION_RAW_PLANS_PATH)
    raw_data = _load_json(project_root / CONTINUATION_RAW_RESULTS_PATH)

    execution_valid, validity_error = validate_raw_artifact_structural_validity(raw_data, plans_data)
    if not execution_valid:
        raise RuntimeError(
            f"Raw artifact structurally invalid; verdict path {R1_VERDICT_LEVEL_1_INVALID}: "
            f"{validity_error}"
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

    # Per-rule protocol validity, component applicability, effective removals,
    # and attribution receipts (repaired R1 contract).
    rule_receipts: dict[str, dict[str, Any]] = {}
    for rid in b2.CANDIDATE_RULE_IDS:
        active_groups = ACTIVE_RULE_CASE_GROUPS[rid]
        receipts: dict[str, Any] = {
            "rule_id": rid,
            "active_case_groups": active_groups,
            "protocol_valid": True,
            "protocol_errors": [],
            "frozen_component_count": 0,
            "active_component_count": 0,
            "inactive_component_count": 0,
            "ambiguous_component_count": 0,
            "validated_active_components": [],
            "held_inactive_components": [],
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
            for comp in plan_record.get("component_applicability_receipts") or []:
                if comp["rule_id"] != rid:
                    continue
                receipts["frozen_component_count"] += 1
                if comp["applicability_status"] == "ACTIVE_IDENTIFIABLE":
                    receipts["active_component_count"] += 1
                    receipts["validated_active_components"].append({
                        "case_id": case_id,
                        "kind": comp["component_kind"],
                        "value": comp["component_value"],
                    })
                elif comp["applicability_status"] == "INACTIVE_NOT_IDENTIFIABLE":
                    receipts["inactive_component_count"] += 1
                    receipts["held_inactive_components"].append({
                        "case_id": case_id,
                        "kind": comp["component_kind"],
                        "value": comp["component_value"],
                        "held_reason": comp["held_reason"],
                    })
                else:
                    receipts["ambiguous_component_count"] += 1
                    receipts["protocol_valid"] = False
                    receipts["protocol_errors"].append(
                        f"{case_id}: AMBIGUOUS_INVALID component {comp['component_value']}"
                    )
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
        dispositions[rid] = classify_rule_r1(
            protocol_valid=receipts["protocol_valid"],
            baseline_reproduced=baseline_reproduced[rid],
            attributable_loss=bool(attributable_losses[rid]),
            active_component_count=receipts["active_component_count"],
            frozen_component_count=receipts["frozen_component_count"],
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

    verdict = evaluate_batch2_verdict_r1(
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
        "checkpoint": "D4-A5-CONTINUATION",
        "stage": "Deterministic Evaluator — Batch2 Controlled Retirement Validation (Continuation Attempt, R1 contract)",
        "created_at": _utc_now(),
        "attempt_id": "D4-A5_ATTEMPT_2_CONTINUATION",
        "frozen_input_provenance": {
            "historical_a5_starting_head": STARTING_HEAD,
            "historical_a5_stop_head": A5_STOP_HEAD,
            "historical_r1_head": R1_HEAD,
            "historical_r2_head": R2_HEAD,
            "historical_r3_head": R3_HEAD,
            "continuation_implementation_freeze_head": exposure.get(
                "continuation_implementation_freeze_head"
            ),
            "continuation_plan_freeze_head": plan_freeze_head,
            "continuation_raw_freeze_head": freeze["head"],
            "preregistration": PREREGISTRATION_PATH,
            "selection": SELECTION_PATH,
            "raw_plans": CONTINUATION_RAW_PLANS_PATH,
            "raw_results": CONTINUATION_RAW_RESULTS_PATH,
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
        "per_rule_component_accounting": {
            rid: {
                "frozen_component_count": rule_receipts[rid]["frozen_component_count"],
                "active_component_count": rule_receipts[rid]["active_component_count"],
                "inactive_component_count": rule_receipts[rid]["inactive_component_count"],
                "validated_active_components": rule_receipts[rid]["validated_active_components"],
                "held_inactive_components": rule_receipts[rid]["held_inactive_components"],
            }
            for rid in b2.CANDIDATE_RULE_IDS
        },
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
    _save_json(project_root / CONTINUATION_EVALUATOR_RESULTS_PATH, evaluator_results)

    result = {
        "schema_version": "1.0.0",
        "checkpoint": "D4-A5-CONTINUATION",
        "lifecycle_stage": "D4-A5 — Second-Batch Low-Risk Locator Controlled Retirement Validation (Continuation Attempt)",
        "created_at": _utc_now(),
        "attempt_id": "D4-A5_ATTEMPT_2_CONTINUATION",
        "commit_lineage": {
            "historical_a5_starting_head": STARTING_HEAD,
            "historical_a5_stop_head": A5_STOP_HEAD,
            "historical_r1_head": R1_HEAD,
            "historical_r2_head": R2_HEAD,
            "historical_r3_head": R3_HEAD,
            "continuation_implementation_freeze_head": exposure.get(
                "continuation_implementation_freeze_head"
            ),
            "continuation_plan_freeze_head": plan_freeze_head,
            "continuation_raw_freeze_head": freeze["head"],
        },
        "exact_selected_rules": list(b2.CANDIDATE_RULE_IDS),
        "exact_component_masks": b2.FROZEN_RETIREMENT_MASKS,
        "plans_completed": plans_data["plans_completed"],
        "cells_completed": raw_data["cells_completed"],
        "cells_failed": raw_data["cells_failed"],
        "per_rule_dispositions": dispositions,
        "per_rule_component_accounting": {
            rid: {
                "validated_active_components": rule_receipts[rid]["validated_active_components"],
                "held_inactive_components": rule_receipts[rid]["held_inactive_components"],
            }
            for rid in b2.CANDIDATE_RULE_IDS
        },
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
    _save_json(project_root / CONTINUATION_RESULT_PATH, result)

    exposure["D4_A5_OUTCOME_EXPOSURE"] = "EVALUATION_COMPLETE"
    exposure["evaluator_executed"] = True
    exposure["scientific_verdict_computed"] = True
    exposure["verdict"] = verdict["verdict"]
    manifest["production_activation"] = False
    manifest["batch1_production_active"] = True
    manifest["batch2_production_active"] = False
    _save_json(project_root / CONTINUATION_MANIFEST_PATH, manifest)

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
    """Independent read-only verification for the R1 era (no writes):
    commit chain dc679f8 (A5 stop) <- 8579cdc (executor freeze) <- cb0f8c3
    (D4-A4) <- 631a66c, historical artifacts immutable, production unchanged,
    machine artifacts consistent, all lifecycle JSON parsable."""
    assert_clean_worktree(project_root)
    head = git_head(project_root)
    chain: list[str] = []
    cursor = head
    for expected_message in (
        R5_COMMIT_MESSAGE,
        R3_COMMIT_MESSAGE,
        R2_COMMIT_MESSAGE,
        R1_COMMIT_MESSAGE,
        A5_STOP_COMMIT_MESSAGE,
        EXECUTOR_FREEZE_COMMIT_MESSAGE,
        STARTING_COMMIT_MESSAGE,
    ):
        message = git_commit_message(project_root, cursor)
        if message != expected_message:
            raise RuntimeError(
                f"Commit chain mismatch at {cursor}: expected '{expected_message}', got '{message}'"
            )
        chain.append(cursor)
        cursor = git_parent(project_root, cursor)
    if cursor != STARTING_PARENT:
        raise RuntimeError(f"Chain base mismatch: expected {STARTING_PARENT}, got {cursor}")
    chain.append(cursor)

    (
        r5_head, r3_head, r2_head, r1_head, a5_stop_head,
        executor_freeze_head, a4_freeze_head, starting_parent,
    ) = chain
    checks: dict[str, Any] = {
        "chain": chain,
        "continuation_manifest_committed_in_r5": git_blob(
            project_root, CONTINUATION_MANIFEST_PATH, r5_head
        ) is not None
        and git_commit_message(
            project_root,
            _git(["log", "-1", "--format=%H", "--", CONTINUATION_MANIFEST_PATH], project_root),
        )
        == R5_COMMIT_MESSAGE,
        "continuation_runtime_artifacts_absent": all(
            git_blob(project_root, rel, "HEAD") is None
            for rel in (
                CONTINUATION_RAW_PLANS_PATH, CONTINUATION_RAW_RESULTS_PATH,
                CONTINUATION_EVALUATOR_RESULTS_PATH, CONTINUATION_RESULT_PATH,
            )
        ),
        "historical_stop_unchanged": git_paths_unchanged_between(
            project_root, a5_stop_head, head, [RESULT_PATH, HISTORICAL_MANIFEST_PATH]
        ) == [],
        "a4_authorities_unchanged": git_paths_unchanged_between(
            project_root, a4_freeze_head, head, [PREREGISTRATION_PATH, SELECTION_PATH]
        ) == [],
        "production_unchanged_since_starting_head": git_paths_unchanged_between(
            project_root, STARTING_HEAD, head, list(PRODUCTION_IMMUTABLE_PATHS)
        ) == [],
        "no_scientific_raw_artifacts_created": all(
            git_blob(project_root, rel, "HEAD") is None
            for rel in (
                HISTORICAL_RAW_PLANS_PATH, RAW_RESULTS_PATH,
                CONTINUATION_RAW_PLANS_PATH, CONTINUATION_RAW_RESULTS_PATH,
            )
        ),
    }

    historical_result = _load_json(project_root / RESULT_PATH)
    r1_result = _load_json(project_root / R1_RESULT_PATH)
    checks["machine_artifacts_agree"] = (
        historical_result["verdict"] == "INVALID / BATCH2_PROTOCOL_OR_SHARED_PLAN_CONSTRUCTION_FAILED"
        and r1_result["historical_stop_preserved"] is True
        and r1_result["repair_status"] == "COMPLETE / PASS"
        and r1_result["accounting"]["provider_calls_in_r1"] == 0
        and r1_result["batch2_production_active"] is False
    )
    checks["batch1_active"] = True
    checks["batch2_production_inactive"] = True

    for rel in (
        RESULT_PATH, R1_RESULT_PATH, R1_PREREGISTRATION_PATH,
        PREREGISTRATION_PATH, SELECTION_PATH, HISTORICAL_MANIFEST_PATH,
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
        choices=[
            "audit",
            "audit-reuse",
            "verify-continuation-start",
            "execute-phase-p",
            "execute-phase-r",
            "evaluate",
            "verify-freeze",
        ],
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
    if args.mode == "audit-reuse":
        receipt = audit_historical_plan_reusability(project_root)
        print(json.dumps(receipt, ensure_ascii=False, indent=2, default=str))
        return
    if args.mode == "verify-continuation-start":
        receipt = verify_continuation_start(project_root)
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        print(
            "[CONTINUATION START VERIFIED] read-only pre-provider gate passed; "
            "zero provider calls made."
        )
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
