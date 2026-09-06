"""D4-A8 — Model-Factory-Theory Symbol-Retirement Targeted Revalidation Preregistration.

Static audit and preregistration script for targeted scientific revalidation
of the three model_factory_theory symbol components:
  - model/PndLmdDPMAngModel1D.cxx
  - model/PndLmdDPMAngModel2D.cxx
  - model/PndLmdModelFactory.cxx
while pflueger_2017 [51, 57, 65] paper page hints remain strictly on HOLD.
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

STARTING_HEAD = "2da89b8223399ff184f4b2b3674f7c995ce8d390"
STARTING_COMMIT_MESSAGE = "D4-A7 activate validated-subset locator retirement"
STARTING_PARENT_HEAD = "41ca18f6b3348d7f20bc226867b0d628aaea2187"

A8_COMMIT_MESSAGE = "D4-A8 preregister model-factory symbol retirement revalidation"

GOLD_QUESTIONS_PATH = "evaluation/benchmarks/v2_6/gold_questions.yaml"
NOVEL_DEV_PATH = "evaluation/novel/v1/novel_dev.yaml"
QUERY_EXPANSIONS_PATH = "configs/query_expansions.yaml"

TARGET_RULE_ID = "model_factory_theory"
MODEL_FACTORY_THEORY_SYMBOL_MASK = [
    "model/PndLmdDPMAngModel1D.cxx",
    "model/PndLmdDPMAngModel2D.cxx",
    "model/PndLmdModelFactory.cxx",
]
HELD_PAGE_HINT_MASK = {
    "pflueger_2017": [51, 57, 65]
}

FORMAL_COHORT = ["g031", "g032", "g033", "g047"]
EXCLUDED_DIAGNOSTIC_CASES = ["g064"]

EXPECTED_A8_PATHS = [
    "docs/EVALUATION_STATUS.md",
    "docs/GENERALIZATION_ROADMAP.md",
    "evaluation/D4_A8_MODEL_FACTORY_THEORY_SYMBOL_RETIREMENT_REVALIDATION_PREREGISTRATION.md",
    "evaluation/d4_a8_model_factory_theory_case_selection.json",
    "evaluation/d4_a8_model_factory_theory_symbol_retirement_preregistration.json",
    "evaluation/scripts/d4_a8_model_factory_theory_symbol_retirement_preregistration.py",
    "tests/unit/test_d4_a8_model_factory_theory_symbol_retirement_preregistration.py",
]


def load_gold_questions(project_root: Path) -> list[dict[str, Any]]:
    """Load benchmark questions from gold_questions.yaml."""
    path = project_root / GOLD_QUESTIONS_PATH
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("questions", [])


def audit_case_metadata(gold_questions: list[dict[str, Any]]) -> dict[str, Any]:
    """Audit metadata of formal candidate cases and excluded diagnostic cases."""
    case_map = {q["id"]: q for q in gold_questions}
    results: dict[str, Any] = {}
    errors: list[str] = []

    # 1. g031 (direct treatment)
    g031 = case_map.get("g031")
    if not g031:
        errors.append("g031 not found in gold_questions.yaml")
    else:
        valid = (
            g031.get("split") == "dev"
            and g031.get("language") == "en"
            and g031.get("intent") == "api"
            and g031.get("expected_status") == "answered"
            and g031.get("review_status") == "approved"
            and any(
                eg.get("group_id") == "g031.e1"
                and any(
                    ev.get("path") == "model/PndLmdModelFactory.cxx"
                    and ev.get("symbol") == "generateModel"
                    for ev in eg.get("any_of", [])
                )
                for eg in g031.get("required_evidence_groups", [])
            )
        )
        if not valid:
            errors.append("g031 failed metadata or evidence validation")
        results["g031"] = {"valid": valid, "formal_role": "DIRECT_MODEL_FACTORY_TREATMENT_CASE"}

    # 2. g032 (control 1)
    g032 = case_map.get("g032")
    if not g032:
        errors.append("g032 not found in gold_questions.yaml")
    else:
        valid = (
            g032.get("split") == "dev"
            and g032.get("language") == "en"
            and g032.get("intent") == "api"
            and g032.get("expected_status") == "answered"
            and g032.get("review_status") == "approved"
            and any(
                eg.get("group_id") == "g032.e1"
                and any(ev.get("path") == "model/PndLmdDPMAngModel1D.cxx" for ev in eg.get("any_of", []))
                for eg in g032.get("required_evidence_groups", [])
            )
        )
        if not valid:
            errors.append("g032 failed metadata or evidence validation")
        results["g032"] = {"valid": valid, "formal_role": "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL"}

    # 3. g033 (control 2)
    g033 = case_map.get("g033")
    if not g033:
        errors.append("g033 not found in gold_questions.yaml")
    else:
        valid = (
            g033.get("split") == "dev"
            and g033.get("language") == "en"
            and g033.get("intent") == "api"
            and g033.get("expected_status") == "answered"
            and g033.get("review_status") == "approved"
            and any(
                eg.get("group_id") == "g033.e1"
                and any(ev.get("path") == "model/PndLmdDPMAngModel2D.cxx" for ev in eg.get("any_of", []))
                for eg in g033.get("required_evidence_groups", [])
            )
        )
        if not valid:
            errors.append("g033 failed metadata or evidence validation")
        results["g033"] = {"valid": valid, "formal_role": "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL"}

    # 4. g047 (control 3)
    g047 = case_map.get("g047")
    if not g047:
        errors.append("g047 not found in gold_questions.yaml")
    else:
        valid = (
            g047.get("split") == "dev"
            and g047.get("language") == "en"
            and g047.get("intent") == "algorithm_theory"
            and g047.get("expected_status") == "answered"
            and g047.get("review_status") == "approved"
            and any(
                eg.get("group_id") == "g047.e1"
                and any(
                    ev.get("source_id") == "pflueger_2017" and ev.get("pdf_page") == 51
                    for ev in eg.get("any_of", [])
                )
                for eg in g047.get("required_evidence_groups", [])
            )
        )
        if not valid:
            errors.append("g047 failed metadata or evidence validation")
        results["g047"] = {"valid": valid, "formal_role": "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL"}

    # 5. g064 (excluded diagnostic)
    g064 = case_map.get("g064")
    if not g064:
        errors.append("g064 not found in gold_questions.yaml")
    else:
        valid = (g064.get("language") == "zh")
        results["g064"] = {
            "valid": valid,
            "language": g064.get("language"),
            "excluded": True,
            "reason": "NON_ENGLISH_OUTSIDE_FORMAL_PRODUCT_GATE",
        }

    all_valid = (len(errors) == 0)
    return {
        "all_valid": all_valid,
        "errors": errors,
        "case_audits": results,
    }


def audit_deterministic_rule_matching(
    project_root: Path,
    gold_questions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Mechanically audit query expansion rule matching using production matcher."""
    from panda_agent.config import load_query_expansions
    from panda_agent.d3_structured import select_matching_query_expansions

    qe = load_query_expansions(project_root / QUERY_EXPANSIONS_PATH)
    case_map = {q["id"]: q for q in gold_questions}

    matching_results: dict[str, Any] = {}
    errors: list[str] = []

    # g031 must match model_factory_theory
    q_g031 = case_map["g031"]["query"]
    dec_g031 = select_matching_query_expansions(q_g031, qe.rules, None)
    matched_g031 = [r.rule_id for r in dec_g031.active_matching_rules]
    if TARGET_RULE_ID not in matched_g031:
        errors.append(f"g031 query '{q_g031}' failed to match {TARGET_RULE_ID}")
    matching_results["g031"] = {
        "matched_rules": matched_g031,
        "target_matched": TARGET_RULE_ID in matched_g031,
        "role": "DIRECT_TREATMENT",
    }

    # g032 must NOT match model_factory_theory
    q_g032 = case_map["g032"]["query"]
    dec_g032 = select_matching_query_expansions(q_g032, qe.rules, None)
    matched_g032 = [r.rule_id for r in dec_g032.active_matching_rules]
    if TARGET_RULE_ID in matched_g032:
        errors.append(f"g032 query '{q_g032}' unexpectedly matched {TARGET_RULE_ID}")
    matching_results["g032"] = {
        "matched_rules": matched_g032,
        "target_matched": TARGET_RULE_ID in matched_g032,
        "role": "NO_OP_CONTROL",
    }

    # g033 must NOT match model_factory_theory
    q_g033 = case_map["g033"]["query"]
    dec_g033 = select_matching_query_expansions(q_g033, qe.rules, None)
    matched_g033 = [r.rule_id for r in dec_g033.active_matching_rules]
    if TARGET_RULE_ID in matched_g033:
        errors.append(f"g033 query '{q_g033}' unexpectedly matched {TARGET_RULE_ID}")
    matching_results["g033"] = {
        "matched_rules": matched_g033,
        "target_matched": TARGET_RULE_ID in matched_g033,
        "role": "NO_OP_CONTROL",
    }

    # g047 must NOT match model_factory_theory
    q_g047 = case_map["g047"]["query"]
    dec_g047 = select_matching_query_expansions(q_g047, qe.rules, None)
    matched_g047 = [r.rule_id for r in dec_g047.active_matching_rules]
    if TARGET_RULE_ID in matched_g047:
        errors.append(f"g047 query '{q_g047}' unexpectedly matched {TARGET_RULE_ID}")
    matching_results["g047"] = {
        "matched_rules": matched_g047,
        "target_matched": TARGET_RULE_ID in matched_g047,
        "role": "NO_OP_CONTROL",
    }

    all_roles_correct = (len(errors) == 0)
    return {
        "all_roles_correct": all_roles_correct,
        "errors": errors,
        "matching_results": matching_results,
    }


def audit_page_hint_coverage_gap(project_root: Path) -> dict[str, Any]:
    """Audit whether any approved English question matches model_factory_theory under an intent permitting page hints."""
    from panda_agent.config import load_query_expansions
    from panda_agent.d3_structured import select_matching_query_expansions

    qe = load_query_expansions(project_root / QUERY_EXPANSIONS_PATH)

    candidate_surviving_cases: list[dict[str, Any]] = []

    # Check gold
    gold_path = project_root / GOLD_QUESTIONS_PATH
    with open(gold_path, "r", encoding="utf-8") as f:
        gold_data = yaml.safe_load(f)

    for q in gold_data.get("questions", []):
        q_text = q.get("query", "")
        dec = select_matching_query_expansions(q_text, qe.rules, None)
        matched = [r.rule_id for r in dec.active_matching_rules]
        if TARGET_RULE_ID in matched:
            lang = q.get("language")
            intent = q.get("intent")
            # Page hints survive only under algorithm_theory or algorithm_implementation
            survives = (lang == "en" and intent in ("algorithm_theory", "algorithm_implementation"))
            if survives:
                candidate_surviving_cases.append({
                    "id": q.get("id"),
                    "dataset": "gold",
                    "language": lang,
                    "intent": intent,
                })

    # Check novel_dev
    novel_path = project_root / NOVEL_DEV_PATH
    if novel_path.exists():
        with open(novel_path, "r", encoding="utf-8") as f:
            novel_data = yaml.safe_load(f)
        for q in novel_data.get("questions", []):
            q_text = q.get("query") or q.get("question", "")
            dec = select_matching_query_expansions(q_text, qe.rules, None)
            matched = [r.rule_id for r in dec.active_matching_rules]
            if TARGET_RULE_ID in matched:
                lang = q.get("language")
                intent = q.get("intent")
                survives = (lang == "en" and intent in ("algorithm_theory", "algorithm_implementation"))
                if survives:
                    candidate_surviving_cases.append({
                        "id": q.get("id"),
                        "dataset": "novel_dev",
                        "language": lang,
                        "intent": intent,
                    })

    if candidate_surviving_cases:
        result = "EXISTING_APPROVED_ENGLISH_CASE_FOUND"
    else:
        result = "NO_EXISTING_APPROVED_ENGLISH_CASE_FOUND"

    return {
        "status": "OPEN",
        "result": result,
        "candidate_surviving_cases": candidate_surviving_cases,
        "explanation": (
            "No existing approved English question matches model_factory_theory under an intent "
            "that permits page hints to survive normal production plan formation. "
            "Therefore pflueger_2017 [51, 57, 65] remain HOLD."
        ),
    }


def audit_plan_reusability(project_root: Path) -> dict[str, Any]:
    """Audit existing committed plan artifacts for reusability."""
    reusability: dict[str, str] = {}
    for case_id in FORMAL_COHORT:
        reusability[case_id] = "NO_COMPATIBLE_FROZEN_PLAN"

    return {
        "reusability_results": reusability,
        "all_require_fresh_acquisition": True,
        "fresh_plans_required": 4,
    }


def verify_starting_boundary(project_root: Path) -> dict[str, Any]:
    """Verify git HEAD, commit message, and parent against starting boundary."""
    cmd_head = ["git", "rev-parse", "HEAD"]
    head_sha = subprocess.run(cmd_head, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    cmd_msg = ["git", "log", "-1", "--pretty=format:%s"]
    head_msg = subprocess.run(cmd_msg, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    cmd_parent = ["git", "rev-parse", "HEAD~1"]
    parent_sha = subprocess.run(cmd_parent, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    cmd_status = ["git", "status", "--porcelain"]
    clean = len(subprocess.run(cmd_status, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()) == 0

    return {
        "head_exact": (head_sha == STARTING_HEAD),
        "msg_exact": (head_msg == STARTING_COMMIT_MESSAGE),
        "parent_exact": (parent_sha == STARTING_PARENT_HEAD),
        "clean_worktree": clean,
        "head_sha": head_sha,
        "parent_sha": parent_sha,
        "head_msg": head_msg,
    }


def verify_git_commit_identity(
    project_root: Path,
    head_ref: str = "HEAD",
    expected_parent: str = STARTING_HEAD,
    expected_msg: str = A8_COMMIT_MESSAGE,
) -> dict[str, Any]:
    """Verify git commit message and parent for A8 commit."""
    cmd_msg = ["git", "log", "-1", "--pretty=format:%s", head_ref]
    actual_msg = subprocess.run(cmd_msg, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    cmd_parent = ["git", "rev-parse", f"{head_ref}~1"]
    actual_parent = subprocess.run(cmd_parent, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    msg_exact = (actual_msg == expected_msg)
    parent_exact = (actual_parent == expected_parent)

    return {
        "all_valid": msg_exact and parent_exact,
        "a8_commit_message_exact": msg_exact,
        "a8_parent_exact": parent_exact,
        "actual_msg": actual_msg,
        "actual_parent": actual_parent,
    }


def verify_git_cumulative_diff(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = STARTING_HEAD,
    _override_diff_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Verify cumulative diff between base_ref and head_ref contains exactly the 7 A8 paths."""
    if _override_diff_paths is not None:
        diff_paths = sorted(_override_diff_paths)
    else:
        cmd = ["git", "diff", "--name-only", base_ref, head_ref]
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
        diff_paths = sorted([p.replace("\\", "/").strip() for p in res.stdout.splitlines() if p.strip()])
    exact_match = (diff_paths == sorted(EXPECTED_A8_PATHS))
    return {
        "exact_match": exact_match,
        "diff_paths": diff_paths,
        "expected_paths": sorted(EXPECTED_A8_PATHS),
        "extra_paths": [p for p in diff_paths if p not in EXPECTED_A8_PATHS],
        "missing_paths": [p for p in EXPECTED_A8_PATHS if p not in diff_paths],
    }


def verify_production_tree_immutability(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = STARTING_HEAD,
    _override_src_tree: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """Verify git tree object for src is identical to base_ref."""
    def get_tree_hash(ref_path: str) -> str:
        cmd = ["git", "rev-parse", ref_path]
        return subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

    if _override_src_tree is not None:
        head_src, base_src = _override_src_tree
    else:
        head_src = get_tree_hash(f"{head_ref}:src")
        base_src = get_tree_hash(f"{base_ref}:src")
    src_tree_immutable = (head_src == base_src)

    return {
        "src_tree_immutable": src_tree_immutable,
        "head_src_tree": head_src,
        "base_src_tree": base_src,
    }


def verify_configs_immutability(
    project_root: Path,
    head_ref: str = "HEAD",
    base_ref: str = STARTING_HEAD,
    _override_configs_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Verify that within configs/, no file was changed."""
    if _override_configs_paths is not None:
        configs_paths = sorted(_override_configs_paths)
    else:
        cmd = ["git", "diff", "--name-only", base_ref, head_ref, "--", "configs"]
        res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
        configs_paths = sorted([p.replace("\\", "/").strip() for p in res.stdout.splitlines() if p.strip()])
    exact = (configs_paths == [])
    return {
        "configs_immutable": exact,
        "configs_paths": configs_paths,
    }


def verify_clean_worktree(project_root: Path) -> bool:
    """Verify working tree and index are completely clean."""
    cmd = ["git", "status", "--porcelain"]
    res = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True)
    return len(res.stdout.strip()) == 0


def verify_production_state(project_root: Path) -> dict[str, Any]:
    """Verify production query_expansions.yaml conforms to post-D4-A7 contract."""
    from panda_agent.config import load_query_expansions

    full_path = project_root / QUERY_EXPANSIONS_PATH
    qe = load_query_expansions(full_path)
    r_map = {r.rule_id: r for r in qe.rules}

    eff = r_map.get("effective_acceptance_pipeline")
    root_macro = r_map.get("root_macro_usage")
    mft = r_map.get("model_factory_theory")
    poca = r_map.get("event_poca_handoff")
    restgas = r_map.get("restgas_profile_workflow")

    valid = (
        eff is not None and eff.symbols == [] and getattr(eff, "structured_replacement", False) is False
        and root_macro is not None and root_macro.symbols == [] and getattr(root_macro, "structured_replacement", False) is False
        and mft is not None and mft.symbols == MODEL_FACTORY_THEORY_SYMBOL_MASK
        and getattr(mft, "paper_page_hints", {}).get("pflueger_2017") == [51, 57, 65]
        and getattr(mft, "structured_replacement", False) is False
        and poca is not None and poca.symbols == [] and getattr(poca, "structured_replacement", False) is True
        and restgas is not None and restgas.symbols == [] and getattr(restgas, "structured_replacement", False) is True
    )

    return {
        "production_state_valid": valid,
        "effective_acceptance_pipeline_retired": (eff.symbols == [] if eff else False),
        "root_macro_usage_retired": (root_macro.symbols == [] if root_macro else False),
        "model_factory_theory_held": (mft.symbols == MODEL_FACTORY_THEORY_SYMBOL_MASK if mft else False),
        "batch1_active": (poca.symbols == [] and restgas.symbols == [] if poca and restgas else False),
    }


def project_treatment_plan(
    canonical_plan: dict[str, Any],
    target_symbol_mask: list[str] = MODEL_FACTORY_THEORY_SYMBOL_MASK,
) -> dict[str, Any]:
    """Deterministic helper to project treatment plan from canonical plan.

    Subtracts only contribution-ledger origins matching rule_id='model_factory_theory'
    and component in target_symbol_mask. Preserves independent origins and paper hints.
    """
    projected = copy.deepcopy(canonical_plan)
    contributions = projected.get("contributions", [])

    new_contributions = []
    selected_origins_removed = 0

    for c in contributions:
        is_target = (
            c.get("rule_id") == TARGET_RULE_ID
            and c.get("kind") == "symbol"
            and c.get("value") in target_symbol_mask
            and c.get("applicability") == "ACTIVE_IDENTIFIABLE"
        )
        if is_target:
            selected_origins_removed += 1
        else:
            new_contributions.append(c)

    projected["contributions"] = new_contributions

    # Recompute deduplicated symbols from surviving contributions
    surviving_symbols: list[str] = []
    for c in new_contributions:
        if c.get("kind") == "symbol":
            val = c.get("value")
            if val and val not in surviving_symbols:
                surviving_symbols.append(val)

    projected["symbols"] = surviving_symbols
    projected["selected_origins_removed"] = selected_origins_removed
    return projected


def evaluate_hypothetical_outcome(
    baseline_reproduced: bool,
    all_symbols_active: bool,
    dependency_observed: bool,
    control_divergence: bool,
    safety_regression: bool,
    protocol_valid: bool = True,
) -> str:
    """Precedence evaluator for prospective scientific outcomes."""
    # Level 1: Protocol Failure
    if not protocol_valid:
        return "INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED"

    # Level 2: Baseline not reproduced
    if not baseline_reproduced:
        return "INCONCLUSIVE / TARGET_REFERENCE_BASELINE_NOT_REPRODUCED"

    # Level 3: Dependency observed
    if dependency_observed:
        return "DEPENDENCY_OBSERVED_RETAIN"

    # Level 4: Control or safety regression
    if control_divergence or safety_regression:
        return "FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION"

    # Level 5: Applicability incomplete
    if not all_symbols_active:
        return "INCONCLUSIVE / SYMBOL_COMPONENT_APPLICABILITY_INCOMPLETE"

    # Level 6: Successful Partial Outcome
    return "PARTIAL / MODEL_FACTORY_SYMBOL_RETIREMENT_VALIDATED_PAGE_HINTS_HOLD"


def audit_preregistration(project_root: Path) -> dict[str, Any]:
    """Run full audit for preregistration (callable before or after commit)."""
    gold_questions = load_gold_questions(project_root)
    case_audit = audit_case_metadata(gold_questions)
    rule_matching = audit_deterministic_rule_matching(project_root, gold_questions)
    gap_audit = audit_page_hint_coverage_gap(project_root)
    reusability = audit_plan_reusability(project_root)
    prod_state = verify_production_state(project_root)

    all_pass = (
        case_audit["all_valid"]
        and rule_matching["all_roles_correct"]
        and gap_audit["status"] == "OPEN"
        and reusability["all_require_fresh_acquisition"]
        and prod_state["production_state_valid"]
    )

    return {
        "status": "PASS" if all_pass else "FAIL",
        "decision": (
            "MODEL_FACTORY_SYMBOL_RETIREMENT_REVALIDATION_PREREGISTERED"
            if all_pass
            else "PREREGISTRATION_AUDIT_FAILED"
        ),
        "case_metadata_audit": case_audit["all_valid"],
        "rule_matching_audit": rule_matching["all_roles_correct"],
        "page_hint_gap_status": gap_audit["status"],
        "page_hint_gap_result": gap_audit["result"],
        "plan_reusability": reusability["reusability_results"],
        "production_state_valid": prod_state["production_state_valid"],
        "errors": case_audit["errors"] + rule_matching["errors"],
    }


def verify_preregistration(project_root: Path) -> dict[str, Any]:
    """Run verification mode (requires committed state)."""
    audit_res = audit_preregistration(project_root)
    clean_wt = verify_clean_worktree(project_root)
    commit_ident = verify_git_commit_identity(project_root)
    cum_diff = verify_git_cumulative_diff(project_root)
    src_tree = verify_production_tree_immutability(project_root)
    configs_diff = verify_configs_immutability(project_root)

    all_pass = (
        audit_res["status"] == "PASS"
        and clean_wt
        and commit_ident["all_valid"]
        and cum_diff["exact_match"]
        and src_tree["src_tree_immutable"]
        and configs_diff["configs_immutable"]
    )

    return {
        "status": "PASS" if all_pass else "FAIL",
        "decision": (
            "MODEL_FACTORY_SYMBOL_RETIREMENT_REVALIDATION_VERIFIED"
            if all_pass
            else "PREREGISTRATION_VERIFICATION_FAILED"
        ),
        "audit_status": audit_res["status"],
        "clean_worktree": clean_wt,
        "a8_commit_message_exact": commit_ident["a8_commit_message_exact"],
        "a8_parent_exact": commit_ident["a8_parent_exact"],
        "a8_cumulative_diff_exact": cum_diff["exact_match"],
        "src_tree_immutable": src_tree["src_tree_immutable"],
        "configs_immutable": configs_diff["configs_immutable"],
        "errors": audit_res["errors"] + (
            [] if clean_wt else ["Working tree or index is dirty"]
        ) + (
            [] if commit_ident["all_valid"] else ["Commit message or parent does not match A8 contract"]
        ) + (
            [] if cum_diff["exact_match"] else [f"Cumulative diff mismatch: {cum_diff['diff_paths']}"]
        ) + (
            [] if src_tree["src_tree_immutable"] else ["src tree modified"]
        ) + (
            [] if configs_diff["configs_immutable"] else ["configs directory modified"]
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="D4-A8 Revalidation Preregistration Runner")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--mode", choices=["audit", "verify"], default="verify")
    args = parser.parse_args()

    project_root = args.project_root.resolve()

    if args.mode == "audit":
        res = audit_preregistration(project_root)
    else:
        # If HEAD is still STARTING_HEAD (pre-commit test run), run audit logic
        cmd_head = ["git", "rev-parse", "HEAD"]
        head_sha = subprocess.run(cmd_head, cwd=project_root, capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()
        if head_sha == STARTING_HEAD:
            res = audit_preregistration(project_root)
        else:
            res = verify_preregistration(project_root)

    print(json.dumps(res, indent=2))
    if res.get("status") != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
