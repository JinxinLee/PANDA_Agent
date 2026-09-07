"""D4-A9-R2: guarded, deterministic post-outcome verification; no science execution.

Synthetic inputs never use repository readers. Live entry points must establish the
prospective verifier checkpoint before opening any outcome-bearing artifact.
"""
from __future__ import annotations

import argparse
import ast
import copy
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
INCIDENT = "1f52957099f3bfd41b9624d863dee0fdddb59ee4"
A9 = "07b8cc921b4e36dc2acf2ae4ba0b27f4b3edf115"
A8 = "06f853d9613c5170676d77261cc2d7b82d50958c"
EXECUTOR = "8e332acb8a1d4658a860ad5e251c9223319bfa42"
PLAN_FREEZE = "443d832258bf99a8f049ea524995b05922cdae80"
RESULT_FREEZE = "2419d4f1818277656c1b3be93e423134e877657f"
PLAN_BLOB = "99891321c0d3ba3e0f54158441f2d739eca2db6f"
RESULT_BLOB = "4f44ac31c9fd917c1212f8d64c59974f90e4cfd6"
FREEZE_MESSAGE = "D4-A9-R2 freeze recovered post-outcome closeout verifier"
CLOSE_MESSAGE = "D4-A9-R2 close recovered post-outcome verification"
STEM = "d4_a9_r2_post_outcome_closeout_verification_recovery"
SCRIPT = f"evaluation/scripts/{STEM}.py"
TEST = f"tests/unit/test_{STEM}.py"
CONTRACT = "evaluation/d4_a9_r2_post_outcome_closeout_verification_contract.json"
REPORT = "evaluation/D4_A9_R2_POST_OUTCOME_CLOSEOUT_VERIFICATION_RECOVERY.md"
RESULT = "evaluation/d4_a9_r2_result.json"
DOCS = ["docs/EVALUATION_STATUS.md", "docs/GENERALIZATION_ROADMAP.md"]
PATHS = sorted([*DOCS, SCRIPT, TEST, CONTRACT, REPORT, RESULT])
SEMANTICS = [SCRIPT, TEST, CONTRACT]
RAW_PLANS_PATH = "evaluation/d4_a9_raw_prospective_plans.json"
RAW_RESULTS_PATH = "evaluation/d4_a9_raw_paired_results.json"
A9_RESULT_PATH = "evaluation/d4_a9_result.json"
A9_EVALUATOR_RESULTS_PATH = "evaluation/d4_a9_evaluator_results.json"
EMBARGO = [RAW_PLANS_PATH, RAW_RESULTS_PATH, A9_RESULT_PATH, A9_EVALUATOR_RESULTS_PATH]
A9_SCRIPT = "evaluation/scripts/d4_a9_model_factory_covered_symbol_retirement_validation.py"
A9_MANIFEST = "evaluation/d4_a9_execution_manifest.json"
A9_PATHS = [*EMBARGO, A9_SCRIPT, A9_MANIFEST,
            "evaluation/D4_A9_MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATION.md",
            "tests/unit/test_d4_a9_model_factory_covered_symbol_retirement_validation.py"]
R1_PATHS = ["evaluation/D4_A9_R1_POST_OUTCOME_CLOSEOUT_VERIFICATION_REPAIR.md",
            "evaluation/d4_a9_r1_post_outcome_closeout_verification_contract.json",
            "evaluation/scripts/d4_a9_r1_post_outcome_closeout_verification_repair.py",
            "tests/unit/test_d4_a9_r1_post_outcome_closeout_verification_repair.py"]
A8_CONTRACT = "evaluation/d4_a8_r2_component_sensitive_execution_preregistration.json"
GOLD = "evaluation/benchmarks/v2_6/gold_questions.yaml"
CASES = ["g031", "g032", "g033", "g047"]
ARMS = ["A7_CURRENT", "COMPONENT_SENSITIVE_MODEL_FACTORY_RETIREMENT"]
TARGET = "model_factory_theory"
INDEPENDENT = "model_factory_acceptance_methods"
COVERED = "model/PndLmdModelFactory.cxx"
HOLD = ["model/PndLmdDPMAngModel1D.cxx", "model/PndLmdDPMAngModel2D.cxx"]
PAGES = {"pflueger_2017": [51, 57, 65]}
VERDICTS = ["INVALID / TARGETED_VALIDATION_PROTOCOL_FAILED",
    "INCONCLUSIVE / ALL_COVERED_COMPONENT_BASELINES_NOT_REPRODUCED",
    "PARTIAL / DEPENDENCY_OBSERVED_FOR_COVERED_COMPONENTS_RETAIN",
    "FAIL / TARGETED_CONTROL_OR_SAFETY_REGRESSION",
    "INCONCLUSIVE / COVERED_COMPONENT_APPLICABILITY_INCOMPLETE",
    "PARTIAL / MODEL_FACTORY_COVERED_SYMBOL_RETIREMENT_VALIDATED_UNCOVERED_COMPONENTS_HOLD"]
ZERO_FIELDS = ["qa_calls", "verifier_calls", "judge_calls", "scientific_evaluator_calls", "retries"]
ROLES = dict(zip(CASES, ["DIRECT_MODEL_FACTORY_TREATMENT_CASE", "DPM1D_SYMBOL_ADJACENT_NONMATCHING_CONTROL",
                        "DPM2D_SYMBOL_ADJACENT_NONMATCHING_CONTROL", "PAGE_HINT_ADJACENT_NONMATCHING_CONTROL"]))


class VerifierNotFrozenError(RuntimeError):
    pass


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root).decode("utf-8").strip()


def git_content(root, ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=root).decode("utf-8")


def changed_paths(root, before, after):
    return sorted(git(root, "diff", "--name-only", before, after).splitlines())


def valid_paths(paths, final=True):
    return sorted(paths) == (PATHS if final else sorted(set(PATHS) - {RESULT}))


def validate_topology(records, final=False):
    errors = []
    if len(records) != (2 if final else 1):
        errors.append("EXACT_COMMIT_COUNT_FAILED")
    parent = INCIDENT
    for record, message in zip(records, [FREEZE_MESSAGE, CLOSE_MESSAGE]):
        if record["parents"] != [parent] or record["message"] != message:
            errors.append("COMMIT_PARENT_OR_MESSAGE_FAILED")
        parent = record["head"]
    return errors


def require_verifier_freeze_checkpoint(root):
    """Metadata only. No raw/artifact content reader is reachable until return."""
    try:
        if git(root, "show", "-s", "--format=%P", INCIDENT) != A9 or git(root, "show", "-s", "--format=%s", INCIDENT) != "D4-A9-R2-Fail":
            raise VerifierNotFrozenError("INCIDENT_BOUNDARY_INVALID")
        heads = git(root, "rev-list", "--reverse", f"{INCIDENT}..HEAD").splitlines()
        if not heads:
            raise VerifierNotFrozenError("VERIFIER_NOT_FROZEN")
        freeze = heads[0]
        record = {"head": freeze, "parents": git(root, "show", "-s", "--format=%P", freeze).split(),
                  "message": git(root, "show", "-s", "--format=%s", freeze)}
        if validate_topology([record]):
            raise VerifierNotFrozenError("FREEZE_TOPOLOGY_INVALID")
        if not valid_paths(changed_paths(root, INCIDENT, freeze), final=False):
            raise VerifierNotFrozenError("FREEZE_SIX_PATHS_INVALID")
        git(root, "merge-base", "--is-ancestor", freeze, "HEAD")
        for path in SEMANTICS:
            original = git(root, "rev-parse", f"{freeze}:{path}")
            if original != git(root, "rev-parse", f"HEAD:{path}") or original != git(root, "hash-object", path):
                raise VerifierNotFrozenError("FROZEN_VERIFIER_SEMANTICS_DRIFT")
        return freeze
    except subprocess.CalledProcessError as exc:
        raise VerifierNotFrozenError("VERIFIER_NOT_FROZEN") from exc


def compare_seal(receipt):
    return bool(receipt["authority_blob"]) and all(
        value == receipt["authority_blob"] for value in receipt["observed_blobs"].values())


def metadata_seals(root):
    """Read Git identities, never raw scientific content. Authority blobs are derived."""
    out = {}
    a8_paths = [p for p in git(root, "ls-tree", "-r", "--name-only", A8).splitlines()
                if "d4_a8_r2_" in p.lower()]
    if len(a8_paths) != 5:
        raise RuntimeError("A8_R2_AUTHORITY_PATH_SET_UNAVAILABLE")
    for label, ref, paths in [("historical_a9", A9, A9_PATHS), ("failed_r1", INCIDENT, R1_PATHS),
                              ("a8_r2", A8, a8_paths), ("gold", EXECUTOR, [GOLD]),
                              ("evaluation_semantics", EXECUTOR, ["src/panda_agent/evaluation.py"])]:
        out[label] = {}
        for path in paths:
            authority = git(root, "rev-parse", f"{ref}:{path}")
            refs = [INCIDENT, "HEAD"] if label == "failed_r1" else [A9, INCIDENT, "HEAD"]
            observations = {r: git(root, "rev-parse", f"{r}:{path}") for r in refs}
            observations["working_tree"] = git(root, "hash-object", path)
            out[label][path] = {"authority_commit": ref, "authority_blob": authority,
                                 "observed_blobs": observations}
    out["raw_freeze"] = {}
    for path, ref, expected in [(RAW_PLANS_PATH, PLAN_FREEZE, PLAN_BLOB),
                               (RAW_RESULTS_PATH, RESULT_FREEZE, RESULT_BLOB)]:
        out["raw_freeze"][path] = {"authority_commit": ref, "authority_blob": expected,
            "observed_blobs": {r: git(root, "rev-parse", f"{r}:{path}")
                               for r in [ref, A9, INCIDENT, "HEAD"]}}
    out["production"] = {}
    for path in ["src", "configs"]:
        out["production"][path] = {"authority_blob": git(root, "rev-parse", f"{A9}:{path}"),
            "observed_blobs": {r: git(root, "rev-parse", f"{r}:{path}") for r in [INCIDENT, "HEAD"]}}
    out["production_worktree_diff"] = git(root, "diff", A9, "--name-only", "--", "src", "configs")
    out["passed"] = not out["production_worktree_diff"] and all(
        compare_seal(receipt) for key, entries in out.items() if isinstance(entries, dict)
        for receipt in entries.values())
    return out


def static_test_isolation(source):
    """Fail-closed whitelist for test IO/calls; aliases and dynamic execution rejected."""
    tree = ast.parse(source)
    errors = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else (
                node.func.attr if isinstance(node.func, ast.Attribute) else "")
            if name in {"open", "read_bytes", "load_gold_dataset", "git_content", "check_output",
                        "system", "popen", "eval", "exec", "getattr", "__import__"}:
                errors.append(f"TEST_IO_OR_DYNAMIC_CALL:{node.lineno}:{name}")
            if name in {"run_live_audit", "verify_committed_closeout"}:
                errors.append(f"DIRECT_LIVE_CALL:{node.lineno}")
            if name == "read_text" and not (isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "test_module_path"):
                errors.append(f"TEST_CONTENT_READ:{node.lineno}")
        if isinstance(node, ast.Name) and node.id in {"RAW_PLANS_PATH", "RAW_RESULTS_PATH", "A9_RESULT_PATH", "A9_EVALUATOR_RESULTS_PATH"}:
            errors.append(f"EMBARGO_CONSTANT:{node.lineno}")
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in EMBARGO:
            errors.append(f"EMBARGO_LITERAL:{node.lineno}")
        if isinstance(node, (ast.Assign, ast.ImportFrom)):
            if any(isinstance(n, ast.Attribute) and n.attr in {"run_live_audit", "verify_committed_closeout"}
                   for n in ast.walk(node)):
                errors.append(f"LIVE_ALIAS:{node.lineno}")
        if isinstance(node, ast.ImportFrom) and any(a.name in {"run_live_audit", "verify_committed_closeout"} for a in node.names):
            errors.append(f"LIVE_IMPORT_ALIAS:{node.lineno}")
    return errors


def assert_prefreeze_rejected(root):
    """Only test bridge to real root: both entrypoints must reject; IO tripwire installed by tests."""
    for entry in [run_live_audit, verify_committed_closeout]:
        try:
            entry(root)
        except VerifierNotFrozenError:
            continue
        raise AssertionError("LIVE_ENTRYPOINT_DID_NOT_REJECT")


def persistence_program_order(source):
    tree = ast.parse(source)
    phase = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "execute_phase_p")
    loop = next(n for n in phase.body if isinstance(n, ast.For))
    saves = [n.lineno for n in loop.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
             and isinstance(n.value.func, ast.Name) and n.value.func.id == "_save_json"
             and n.value.args and isinstance(n.value.args[0], ast.Name) and n.value.args[0].id == "raw_plans_path"]
    gates = [n.lineno for n in loop.body if isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
             and isinstance(n.test.left, ast.Name) and n.test.left.id == "cid"]
    downstream_guard = any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Attribute) and t.attr == "analyze" for t in n.targets)
                           and isinstance(n.value, ast.Name) and n.value.id == "_forbidden_analyze" for n in ast.walk(tree))
    downstream_raise = any(isinstance(n, ast.FunctionDef) and n.name == "_forbidden_analyze"
                           and any(isinstance(v, ast.Raise) for v in n.body) for n in ast.walk(tree))
    return {"passed": bool(saves and gates and min(saves) < min(gates) and downstream_guard and downstream_raise),
            "zero_downstream_analyzer_program_guard": downstream_guard and downstream_raise,
            "first_save_line": min(saves) if saves else None, "formal_gate_line": min(gates) if gates else None,
            "executor_commit": EXECUTOR, "proof": "Frozen program order plus persisted_at <= gated_at receipts; no disk reload claim."}


def plan_signature(plan):
    """Exact A5 compute_plan_signature JSON semantics, without importing executable A5 code."""
    return json.dumps({"intent": plan.get("intent", ""),
        "target_repositories": sorted(plan.get("target_repositories", [])),
        "symbols": sorted(plan.get("symbols", [])),
        "normalized_concepts": sorted(c.strip().casefold() for c in plan.get("concepts", [])),
        "required_source_types": sorted(plan.get("required_source_types", [])),
        "paper_page_hints": [[k, sorted(v)] for k, v in sorted((plan.get("paper_page_hints") or {}).items())],
        "concept_scopes": [[k, v] for k, v in sorted((plan.get("concept_scopes") or {}).items())]}, sort_keys=True)


def source_types(item, lookup):
    """Existing deterministic_metrics source_type semantics, kept local and pure."""
    canonical = lookup.get(item.get("object_id"), item)
    source = str(canonical.get("source_id", ""))
    kind = str(canonical.get("object_type", ""))
    path = str((canonical.get("locator") or {}).get("path") or "").replace("\\", "/")
    if source in {"li_2026", "karavdina_2015", "pflueger_2017"}:
        values = {"paper"}
    elif "sphinx" in source or kind.startswith("sphinx") or path.lower().startswith(("docs/", "doc/")):
        values = {"documentation"}
    elif kind in {"readme_section", "readme_section_chunk"} or path.lower().split("/")[-1].startswith("readme"):
        values = {"readme", "documentation"}
    elif kind in {"workflow", "python_script", "shell_script"}:
        values = {"workflow"}
    elif kind == "relation" or "graph" in item.get("retrieval_channels", []):
        values = {"graph"}
    else:
        values = {"code"}
    return values | (set(item.get("retrieval_channels", [])) & {"workflow", "graph"})


def audit_synthetic_fixture(plans, results, gold, lookup, authority, historical_accounting, program_order):
    """Pure object-input evaluator, equally used for synthetic and guarded live data."""
    from panda_agent.evaluation import _matched_evidence_groups
    errors = []
    def require(condition, label):
        if not condition:
            errors.append(label)
    pp, ss = plans.get("plans", []), results.get("slots", [])
    require(all(plans.get(k) == 4 for k in ["plans_planned", "plans_recorded", "plans_completed"]), "PLAN_HEADER_COUNTS")
    require(results.get("slots_planned") == results.get("slots_completed") == 8, "SLOT_HEADER_COUNTS")
    require([p.get("case_id") for p in pp] == CASES, "EXACT_FOUR_PLANS")
    schedule = [(c, a) for c in CASES for a in ARMS]
    require([(s.get("case_id"), s.get("arm")) for s in ss] == schedule, "EXACT_EIGHT_SCHEDULE")
    require(authority["formal_case_order"] == CASES and authority["covered_symbol_mask"] == [COVERED]
        and authority["uncovered_symbol_hold_mask"] == HOLD and authority["page_hint_hold_mask"] == PAGES,
        "FROZEN_COHORT_OR_MASK")
    require(program_order.get("passed") is True, "PERSISTENCE_PROGRAM_ORDER")
    require(all(c in gold for c in CASES), "GOLD_MISSING")
    by_case = {p.get("case_id"): p for p in pp}
    counts = {"analyzer_calls": 0, "analyzer_provider_attempts": 0,
              "embedding_calls": 0, "reranker_calls": 0, "retrieval_provider_attempts": 0, "token_usage": 0}
    per_case, projection_receipts = {}, {}
    for p in pp:
        cid = p.get("case_id")
        require(p.get("role") == ROLES.get(cid), f"CASE_ROLE:{cid}")
        required = authority["persistence_before_gate_contract"]["required_persisted_fields"]
        require(all(k in p for k in required), f"PLAN_FIELDS:{cid}")
        canonical = p.get("canonical_plan", {})
        require(p.get("raw_analyzer_response") == canonical == p.get("current_execution_projection"), f"CANONICAL:{cid}")
        require(p.get("canonical_serialization") == json.dumps(canonical, sort_keys=True), f"SERIALIZATION:{cid}")
        require(p.get("plan_signature") == plan_signature(canonical), f"SIGNATURE:{cid}")
        require(p.get("provider_model_contract") == authority["future_model_contract"], f"MODEL_CONTRACT:{cid}")
        try:
            persisted = dt.datetime.fromisoformat(p["persisted_at"].replace("Z", "+00:00"))
            gated = dt.datetime.fromisoformat(p["gated_at"].replace("Z", "+00:00"))
            require(persisted <= gated, f"TIMESTAMP_ORDER:{cid}")
        except (KeyError, ValueError, TypeError):
            errors.append(f"TIMESTAMP_MISSING_OR_INVALID:{cid}")
        require(p.get("persistence_state") == "RETRIEVAL_ELIGIBLE", f"PERSISTENCE_STATE:{cid}")
        matched = p.get("matched_rule_identities", [])
        require(matched == (canonical.get("analysis_diagnostics") or {}).get("matched_expansion_rules", []), f"MATCHED_RULE_RECEIPT:{cid}")
        acc = p.get("provider_accounting", {})
        for k in ZERO_FIELDS:
            require(acc.get(k, 0) == 0, f"PLAN_FORBIDDEN_PROVIDER:{cid}:{k}")
        require(acc.get("analyzer_logical_calls") == 1 and acc.get("analyzer_provider_attempts") == 1
                and acc.get("retries") == 0, f"ANALYZER_ACCOUNTING:{cid}")
        for k in ["model_id", "location", "temperature", "retries"]:
            require(acc.get(k) == authority["future_model_contract"][k], f"ANALYZER_MODEL:{cid}:{k}")
        counts["analyzer_calls"] += acc.get("analyzer_logical_calls", 0)
        counts["analyzer_provider_attempts"] += acc.get("analyzer_provider_attempts", 0)
        counts["token_usage"] += acc.get("token_usage", 0)
        per_case[cid] = {"logical_calls": acc.get("analyzer_logical_calls"), "attempts": acc.get("analyzer_provider_attempts"),
                         "tokens": acc.get("token_usage"), "successful_plan_persisted": p.get("persistence_state") == "RETRIEVAL_ELIGIBLE"}
        diff = p.get("treatment_execution_projection_diff_receipts", {})
        removed = diff.get("removed_rule_origin_entries", [])
        trt = p.get("treatment_execution_projection")
        if cid == "g031":
            ledger = [e for e in p.get("contribution_ledger", []) if e.get("kind") == "symbol" and e.get("value") == COVERED]
            require(TARGET in matched and len(ledger) == 1 and len(removed) == 1, "SELECTED_ORIGIN_STRUCTURE")
            origins = ledger[0].get("provenance_origin_ids", []) if len(ledger) == 1 else []
            independent = [o for o in origins if o != TARGET]
            entry = removed[0] if len(removed) == 1 else {}
            require(TARGET in origins and INDEPENDENT in independent, "INDEPENDENT_ORIGIN_MISSING")
            require(entry.get("value") == COVERED and entry.get("kind") == "symbol"
                    and entry.get("retired_rule_origins") == [TARGET]
                    and entry.get("surviving_independent_origins") == independent
                    and entry.get("effectively_removed") is False, "SELECTED_ORIGIN_SUBTRACTION")
            survivors = diff.get("surviving_independent_origin_entries", [])
            require(len(survivors) == 1 and survivors[0].get("value") == COVERED
                    and survivors[0].get("surviving_independent_origins") == independent, "SURVIVING_ORIGIN_RECEIPT")
            require(diff.get("mask_entry_count") == 1 and diff.get("effective_removal_count") == 0,
                    "SELECTED_MASK_RECEIPT")
            require(trt == canonical and COVERED in canonical.get("symbols", []), "INDEPENDENT_ORIGIN_PROJECTION")
        else:
            require(TARGET not in matched and diff.get("mask_entry_count") == 0 and removed == []
                    and diff.get("effective_removal_count") == 0 and trt == canonical, f"CONTROL_NO_OP:{cid}")
        projection_receipts[cid] = copy.deepcopy(diff)
    analyzer_tokens = counts["token_usage"]
    for i, s in enumerate(ss, 1):
        cid, arm = s.get("case_id"), s.get("arm")
        p = by_case.get(cid, {})
        require(s.get("role") == p.get("role") == ROLES.get(cid) and s.get("question") == p.get("question"), f"SLOT_ROLE_QUESTION:{i}")
        require(s.get("cell_index") == i and s.get("cell_id") == f"{cid}_{arm}" and s.get("status") == "COMPLETED", f"SLOT_IDENTITY:{i}")
        require(s.get("canonical_plan_id") == p.get("plan_id") and s.get("canonical_plan_signature") == p.get("plan_signature")
                and s.get("frozen_canonical_plan") == p.get("canonical_plan"), f"SHARED_PLAN:{i}")
        expected = p.get("current_execution_projection" if arm == ARMS[0] else "treatment_execution_projection")
        require(s.get("actual_plan_used") == s.get("arm_execution_projection") == expected
                and s.get("plan_equality_arm_projection_verified") is True, f"PLAN_PROJECTION:{i}")
        require(s.get("final_evidence_object_ids") == [e.get("object_id") for e in s.get("evidence_items", [])], f"FINAL_EVIDENCE_IDENTITY:{i}")
        acc = s.get("provider_accounting", {})
        require(acc.get("embedding_calls") == 1 and acc.get("generation_calls") == 1 and acc.get("model_calls") == 2,
                f"RETRIEVAL_ACCOUNTING:{i}")
        for k in [*ZERO_FIELDS, "analyzer_calls", "analyzer_provider_attempts"]:
            require(acc.get(k, 0) == 0, f"DOWNSTREAM_PROVIDER:{i}:{k}")
        counts["embedding_calls"] += acc.get("embedding_calls", 0)
        counts["reranker_calls"] += acc.get("generation_calls", 0)
        counts["retrieval_provider_attempts"] += acc.get("model_calls", 0)
        counts["token_usage"] += acc.get("token_usage", 0)
    pa, ra = plans.get("accounting", {}), results.get("accounting", {})
    for k in ["analyzer_calls", "analyzer_provider_attempts"]:
        require(pa.get(k) == counts[k], f"PLAN_SUMMARY:{k}")
    require(pa.get("token_usage") == analyzer_tokens, "PLAN_TOKEN_SUMMARY")
    for k in ["embedding_calls", "reranker_calls"]:
        require(ra.get(k) == counts[k], f"RESULT_SUMMARY:{k}")
    require(ra.get("model_calls") == counts["retrieval_provider_attempts"] and ra.get("token_usage") == counts["token_usage"] - analyzer_tokens, "RESULT_ATTEMPTS_TOKENS")
    for k in ZERO_FIELDS:
        require(historical_accounting.get(k) == 0, f"A9_ZERO_ACCOUNTING:{k}")
        require(pa.get(k, 0) == 0 and ra.get(k, 0) == 0, f"RAW_ZERO_ACCOUNTING:{k}")
        counts[k] = historical_accounting.get(k)
    for k in ["analyzer_calls", "analyzer_provider_attempts", "embedding_calls", "reranker_calls", "token_usage"]:
        require(historical_accounting.get(k) == counts[k], f"A9_ACCOUNTING:{k}")
    counts["total_logical_calls"] = counts["analyzer_calls"] + counts["embedding_calls"] + counts["reranker_calls"]
    counts["total_attempts"] = counts["analyzer_provider_attempts"] + counts["retrieval_provider_attempts"]
    require(counts["total_logical_calls"] == counts["total_attempts"] == authority["derived_provider_budget"]["total_logical_model_calls"], "TOTAL_PROVIDER_ACCOUNTING")
    output = {"errors": errors, "formal_cohort": CASES, "target_rule": TARGET, "covered_symbol_mask": [COVERED],
        "hold_masks": {"symbols": HOLD, "paper_pages": PAGES},
        "matched_rules": {p.get("case_id"): p.get("matched_rule_identities") for p in pp},
        "analyzer_accounting": {"per_case": per_case, "total_tokens": analyzer_tokens},
        "provider_accounting": counts, "projection_receipts": projection_receipts,
        "persistence_program_order": program_order}
    if errors:
        return finish(output, 1)
    critical, grounding, versions, variance = {}, {}, {}, {}
    slot_map = {(s["case_id"], s["arm"]): s for s in ss}
    for cid in CASES:
        q = gold[cid]
        critical[cid], grounding[cid], versions[cid] = {}, {}, {}
        for arm in ARMS:
            s = slot_map[cid, arm]
            ids = s["final_evidence_object_ids"]
            groups = [g for g in q.required_evidence_groups if g.critical]
            if cid == "g031":
                groups = [g for g in groups if g.group_id == "g031.e1"]
            if not groups:
                errors.append(f"SAFETY_CONTRACT_NOT_MECHANICALLY_REPRODUCIBLE:{cid}")
            recall, provenance = _matched_evidence_groups(groups, ids, lookup)
            for receipt in provenance:
                if receipt.get("object_id") in ids:
                    receipt["final_evidence_position_1based"] = ids.index(receipt["object_id"]) + 1
            critical[cid][arm] = {"recall": recall, "matched_groups": [r["group_id"] for r in provenance if r.get("object_id")], "provenance": provenance}
            violations, resolved, unresolved, forbidden, version_items = [], [], [], [], []
            observed_source_types = set()
            for item in s["evidence_items"]:
                observed_source_types.update(source_types(item, lookup))
                oid = item.get("object_id")
                canonical = lookup.get(oid)
                identity = {k: (canonical or item).get(k) for k in ["object_id", "source_id", "source_version_id"]}
                if canonical is None:
                    unresolved.append(identity)
                    violations.append({"identity": identity, "kind": "UNRESOLVED_OBJECT"})
                else:
                    resolved.append(identity)
                    if any(item.get(k) != canonical.get(k) for k in ["source_id", "source_version_id"]):
                        violations.append({"identity": identity, "kind": "CANONICAL_SOURCE_IDENTITY_MISMATCH"})
                # Existing Gold forbidden selector matches evidence metadata directly.
                for index, selector in enumerate(q.forbidden_evidence):
                    if selector.matches(item):
                        hit = {"identity": identity, "kind": "FORBIDDEN_EVIDENCE", "selector_index": index}
                        forbidden.append(hit)
                        violations.append(hit)
                version = item.get("source_version_id")
                state = "VALID_VERSION" if version in q.allowed_source_versions else (
                    "VERSION_ID_MISSING_INVALID" if version is None else "VERSION_VIOLATION")
                version_items.append({"object_id": oid, "source_id": item.get("source_id"), "source_version_id": version, "state": state})
            missing_types = sorted(set(q.required_source_types) - observed_source_types)
            violations.extend({"identity": {"required_source_type": t}, "kind": "MISSING_REQUIRED_SOURCE_TYPE"} for t in missing_types)
            grounding[cid][arm] = {"resolved": resolved, "unresolved": unresolved, "forbidden": forbidden, "violations": violations,
                                   "source_types": sorted(observed_source_types), "missing_required_source_types": missing_types}
            versions[cid][arm] = {"items": version_items, "valid": sum(v["state"] == "VALID_VERSION" for v in version_items),
                "violations": sum(v["state"] == "VERSION_VIOLATION" for v in version_items),
                "missing_invalid": sum(v["state"] == "VERSION_ID_MISSING_INVALID" for v in version_items), "not_governed": 0}
        current_violations = {json.dumps(v, sort_keys=True) for v in grounding[cid][ARMS[0]]["violations"]}
        grounding[cid]["treatment_only_regressions"] = [v for v in grounding[cid][ARMS[1]]["violations"] if json.dumps(v, sort_keys=True) not in current_violations]
        current_groups = critical[cid][ARMS[0]]["matched_groups"]
        critical[cid]["lost_groups"] = sorted(set(current_groups) - set(critical[cid][ARMS[1]]["matched_groups"]))
        critical[cid]["delta"] = critical[cid][ARMS[1]]["recall"] - critical[cid][ARMS[0]]["recall"]
        cur = slot_map[cid, ARMS[0]]["final_evidence_object_ids"]
        trt = slot_map[cid, ARMS[1]]["final_evidence_object_ids"]
        # Exclude every object matching a critical group, not only the first matched witness.
        crit_groups = [g for g in q.required_evidence_groups if g.critical]
        crit_ids = {oid for oid in set(cur + trt) if any(r.get("object_id") for r in _matched_evidence_groups(crit_groups, [oid], lookup)[1])}
        variance[cid] = {"diagnostic_only": True, "evidence_set_equal": set(cur) == set(trt), "rank_order_equal": cur == trt,
            "noncritical_additions": sorted(set(trt) - set(cur) - crit_ids), "noncritical_removals": sorted(set(cur) - set(trt) - crit_ids)}
    output.update(critical_safety=critical, grounding_safety=grounding, version_safety=versions, diagnostic_noncritical_variance=variance)
    baseline = "g031.e1" in critical["g031"][ARMS[0]]["matched_groups"]
    treatment = "g031.e1" in critical["g031"][ARMS[1]]["matched_groups"]
    output["g031_baseline_result"] = critical["g031"][ARMS[0]]
    output["g031_treatment_result"] = critical["g031"][ARMS[1]]
    output["selected_origin_subtraction"] = projection_receipts["g031"]["removed_rule_origin_entries"]
    output["independent_origin_preservation"] = projection_receipts["g031"].get("surviving_independent_origin_entries", [])
    safety = any(critical[c]["lost_groups"] for c in CASES[1:]) or any(grounding[c]["treatment_only_regressions"] for c in CASES) or any(
        versions[c][a]["violations"] + versions[c][a]["missing_invalid"] for c in CASES for a in ARMS)
    app = [r for r in by_case["g031"]["component_applicability_receipts"] if r.get("component_value") == COVERED]
    if any(r.get("applicability_status") == "AMBIGUOUS_INVALID" for r in app):
        errors.append("AMBIGUOUS_APPLICABILITY")
    level = 1 if errors else 2 if not baseline else 3 if not treatment else 4 if safety else 5 if (
        len(app) != 1 or app[0].get("applicability_status") != "ACTIVE_IDENTIFIABLE") else 6
    return finish(output, level)


def finish(output, level):
    disposition = ["INVALID_PROTOCOL", "INCONCLUSIVE_BASELINE_NOT_REPRODUCED", "DEPENDENCY_OBSERVED_RETAIN",
                   "RETIREMENT_VALIDATED_COMPONENT", "INCONCLUSIVE_APPLICABILITY_INCOMPLETE", "RETIREMENT_VALIDATED_COMPONENT"][level - 1]
    output.update(verification_status="FAIL" if output["errors"] else "PASS", scientific_verdict_level=level,
        scientific_verdict=VERDICTS[level - 1], scientific_decision=VERDICTS[level - 1].split(" / ", 1)[1],
        component_dispositions={COVERED: disposition, **{s: "HOLD_DIRECT_TREATMENT_COVERAGE_GAP" for s in HOLD},
                                "pflueger_2017:[51,57,65]": "HOLD_OUTSIDE_TREATMENT_SCOPE"})
    for k in ["shared_plan_integrity", "persistence_integrity", "schedule_integrity", "plan_projection_integrity", "provider_accounting_integrity"]:
        output[k] = not output["errors"]
    return output


def compare_result_core(committed, fresh):
    return [] if committed == fresh else ["D4_A9_R2_MACHINE_RESULT_DRIFT"]


def contract_audit(root):
    contract = json.loads((root / CONTRACT).read_text(encoding="utf-8"))
    errors = static_test_isolation((root / TEST).read_text(encoding="utf-8"))
    tree = ast.parse((root / SCRIPT).read_text(encoding="utf-8"))
    for name in ["run_live_audit", "verify_committed_closeout"]:
        body = next(n.body for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
        first = body[0]
        if not (isinstance(first, ast.Assign) and isinstance(first.value, ast.Call)
                and isinstance(first.value.func, ast.Name) and first.value.func.id == "require_verifier_freeze_checkpoint"):
            errors.append(f"LIVE_GUARD_NOT_FIRST:{name}")
    required = {"recovery_from_failed_r1_attempt": True, "starting_incident_commit": INCIDENT,
        "incident_commit_is_not_scientific_r2_authority": True, "verification_only": True,
        "zero_scientific_provider": True, "real_data_access_before_verifier_freeze": "forbidden",
        "production_activation_authorized": False, "D4_A10_authorized": False}
    errors += [f"CONTRACT:{k}" for k, v in required.items() if contract.get(k) != v]
    a8 = json.loads(git_content(root, A8, A8_CONTRACT))
    if a8["formal_case_order"] != CASES or a8["covered_symbol_mask"] != [COVERED] or a8["uncovered_symbol_hold_mask"] != HOLD or a8["page_hint_hold_mask"] != PAGES:
        errors.append("AUTHORITY_MASK_DRIFT")
    if [v.split(": ", 1)[1] for v in a8["overall_outcome_precedence"]] != VERDICTS:
        errors.append("AUTHORITY_PRECEDENCE_DRIFT")
    order = persistence_program_order(git_content(root, EXECUTOR, A9_SCRIPT))
    if not order["passed"]:
        errors.append("FROZEN_PERSISTENCE_ORDER")
    return {"verification_status": "FAIL" if errors else "PASS", "errors": errors, "outcome_files_read": 0, "persistence_order": order}


def run_live_audit(root):
    freeze = require_verifier_freeze_checkpoint(root)  # MUST remain first executable statement.
    seals = metadata_seals(root)
    if not seals["passed"]:
        raise RuntimeError("HISTORICAL_SCIENTIFIC_OR_INCIDENT_ARTIFACT_DRIFT")
    import yaml
    from panda_agent.evaluation import GoldDataset
    authority = json.loads(git_content(root, A8, A8_CONTRACT))
    plans = json.loads(git_content(root, PLAN_FREEZE, RAW_PLANS_PATH))
    results = json.loads(git_content(root, RESULT_FREEZE, RAW_RESULTS_PATH))
    historical = json.loads(git_content(root, A9, A9_RESULT_PATH))
    gold = GoldDataset.model_validate(yaml.safe_load(git_content(root, EXECUTOR, GOLD)))
    # Same local canonical catalog selection as evaluation_runner.load_object_lookup.
    reports = list((root / "data" / "normalized").glob("*/ingestion_report.json"))
    if not reports:
        raise RuntimeError("SAFETY_CONTRACT_NOT_MECHANICALLY_REPRODUCIBLE: canonical lookup unavailable")
    lookup_path = max(reports, key=lambda p: p.stat().st_mtime).parent / "knowledge_objects.jsonl"
    lookup = {item["object_id"]: item for line in lookup_path.read_text(encoding="utf-8").splitlines() if line.strip() for item in [json.loads(line)]}
    order = persistence_program_order(git_content(root, EXECUTOR, A9_SCRIPT))
    result = audit_synthetic_fixture(plans, results, {q.id: q for q in gold.questions}, lookup, authority,
                                     historical["provider_accounting"], order)
    if (historical.get("formal_cohort") != CASES or historical.get("covered_symbol_mask") != [COVERED]
            or historical.get("uncovered_symbol_hold_mask") != HOLD or historical.get("page_hint_hold_mask") != PAGES
            or historical.get("production_activation_authorized") is not False):
        result["errors"].append("HISTORICAL_A9_CONTRACT_OR_ACTIVATION_DRIFT")
        finish(result, 1)
    # Seal identities are checked again at verify; omit changing HEAD labels from stable result core.
    stable_seals = {k: {p: {"authority_commit": r.get("authority_commit"), "authority_blob": r["authority_blob"], "verified": compare_seal(r)}
                        for p, r in entries.items()} for k, entries in seals.items() if isinstance(entries, dict)}
    result.update(lifecycle_stage="D4-A9-R2", starting_incident_head=INCIDENT, verifier_freeze_head=freeze,
        first_live_audit_after_freeze=True, first_live_audit_command=f"python {SCRIPT} --project-root . --mode live-audit",
        verification_only=True, scientific_provider_calls=0, scientific_tokens=0, scientific_retries=0, db_writes=0,
        scientific_execution_path="No provider or retrieval constructors/imports; deterministic local inputs only",
        git_seals=stable_seals, production_immutable=seals["passed"],
        local_lookup_path=lookup_path.relative_to(root).as_posix(),
        production_activation_authorized=False, D4_A10_authorized=False,
        historical_manifest_supersession={"classification": "HISTORICAL_RECEIPT_STALE_NON_AUTHORITATIVE",
            "prospective_plans_frozen": compare_seal(seals["raw_freeze"][RAW_PLANS_PATH]),
            "paired_results_frozen": compare_seal(seals["raw_freeze"][RAW_RESULTS_PATH]),
            "retrieval_slots_completed": sum(s.get("status") == "COMPLETED" for s in results["slots"]),
            "evaluation_execution_recorded_in_git": bool(git(root, "rev-parse", f"{A9}:{A9_EVALUATOR_RESULTS_PATH}"))})
    return result


def verify_committed_closeout(root):
    freeze = require_verifier_freeze_checkpoint(root)
    heads = git(root, "rev-list", "--reverse", f"{INCIDENT}..HEAD").splitlines()
    records = [{"head": h, "parents": git(root, "show", "-s", "--format=%P", h).split(), "message": git(root, "show", "-s", "--format=%s", h)} for h in heads]
    errors = validate_topology(records, final=True)
    if not valid_paths(changed_paths(root, INCIDENT, "HEAD")):
        errors.append("EXACT_SEVEN_PATHS_FAILED")
    if git(root, "status", "--porcelain"):
        errors.append("UNCLEAN_CLOSEOUT")
    for path in DOCS:
        if git_content(root, INCIDENT, path) not in (root / path).read_text(encoding="utf-8"):
            errors.append(f"INCIDENT_DOCUMENTATION_REWRITTEN:{path}")
    if errors:
        return {"verification_status": "FAIL", "errors": errors}
    committed = json.loads(git_content(root, "HEAD", RESULT))
    fresh = run_live_audit(root)
    errors.extend(compare_result_core(committed, fresh))
    if fresh["verification_status"] != "PASS":
        errors.extend(fresh["errors"])
    return {"verification_status": "FAIL" if errors else "PASS", "errors": errors,
            "verifier_freeze_head": freeze, "scientific_verdict_level": fresh["scientific_verdict_level"],
            "scientific_verdict": fresh["scientific_verdict"], "committed_result_equals_live_audit": committed == fresh}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--mode", choices=["contract-audit", "live-audit", "verify"], required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    if args.mode == "contract-audit":
        result = contract_audit(root)
    elif args.mode == "live-audit":
        if (root / RESULT).exists():
            raise RuntimeError("R2_RESULT_ALREADY_EXISTS: use committed verify")
        result = run_live_audit(root)
        (root / RESULT).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        result = verify_committed_closeout(root)
    print(json.dumps({k: v for k, v in result.items() if k in ["verification_status", "errors", "scientific_verdict_level", "scientific_verdict", "verifier_freeze_head", "committed_result_equals_live_audit", "outcome_files_read"]}, indent=2))
    return 0 if result["verification_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
