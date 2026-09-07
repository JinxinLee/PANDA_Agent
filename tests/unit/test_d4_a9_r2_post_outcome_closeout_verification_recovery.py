"""Outcome-blind fixtures only. The real root is used exclusively for guard rejection."""
import builtins
import copy
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "evaluation" / "scripts"))
import d4_a9_r2_post_outcome_closeout_verification_recovery as r
from panda_agent.evaluation import GoldEvidenceGroup, GoldEvidenceSelector


@pytest.fixture(autouse=True)
def embargo(monkeypatch):
    original_builtin, original_io = builtins.open, io.open
    def check(file):
        if isinstance(file, (str, Path)) and any(str(file).replace("\\", "/").endswith(p) for p in r.EMBARGO):
            raise AssertionError("REAL_SCIENTIFIC_FILE_OPEN_FORBIDDEN")
    def guarded_builtin(file, *args, **kwargs):
        check(file)
        return original_builtin(file, *args, **kwargs)
    def guarded_io(file, *args, **kwargs):
        check(file)
        return original_io(file, *args, **kwargs)
    def forbidden_git_reader(*args, **kwargs):
        raise AssertionError("GIT_CONTENT_READER_FORBIDDEN_IN_TESTS")
    monkeypatch.setattr(builtins, "open", guarded_builtin)
    monkeypatch.setattr(io, "open", guarded_io)
    monkeypatch.setattr(r, "git_content", forbidden_git_reader)


@pytest.fixture
def bundle():
    fields = ["case_id", "question", "provider_model_contract", "raw_analyzer_response", "canonical_plan",
              "canonical_serialization", "contribution_ledger", "provenance_origin_receipts",
              "component_applicability_receipts", "current_execution_projection", "treatment_execution_projection",
              "plan_signature", "provider_accounting", "matched_rule_identities"]
    model = {"model_id": "synthetic-model", "temperature": 0.0, "location": "synthetic-location", "retries": 0}
    authority = {"formal_case_order": r.CASES, "covered_symbol_mask": [r.COVERED], "uncovered_symbol_hold_mask": r.HOLD,
        "page_hint_hold_mask": r.PAGES, "future_model_contract": model,
        "persistence_before_gate_contract": {"required_persisted_fields": fields},
        "derived_provider_budget": {"total_logical_model_calls": 20}}
    plans, slots, gold, lookup = [], [], {}, {}
    for cid in r.CASES:
        oid = f"synthetic.{cid}"
        item = {"object_id": oid, "source_id": "synthetic_source", "source_version_id": "synthetic_v1",
                "object_type": "function", "locator": {"path": f"synthetic/{cid}.cxx"}}
        lookup[oid] = item
        gold[cid] = SimpleNamespace(required_evidence_groups=[GoldEvidenceGroup(group_id=f"{cid}.e1", critical=True,
            any_of=[GoldEvidenceSelector(object_id=oid)])], forbidden_evidence=[], allowed_source_versions=["synthetic_v1"], required_source_types=[])
        matched = [r.TARGET, r.INDEPENDENT] if cid == "g031" else []
        canonical = {"symbols": [r.COVERED] if cid == "g031" else [], "analysis_diagnostics": {"matched_expansion_rules": matched}}
        ledger = [{"kind": "symbol", "value": r.COVERED, "contribution_id": f"symbol::{r.COVERED}",
                   "provenance_origin_ids": [r.TARGET, r.INDEPENDENT]}] if cid == "g031" else []
        removed = [{"kind": "symbol", "value": r.COVERED, "retired_rule_origins": [r.TARGET],
                    "surviving_independent_origins": [r.INDEPENDENT], "effectively_removed": False}] if cid == "g031" else []
        diff = {"mask_entry_count": int(cid == "g031"), "removed_rule_origin_entries": removed, "effective_removal_count": 0,
                "surviving_independent_origin_entries": [{"value": r.COVERED, "surviving_independent_origins": [r.INDEPENDENT]}] if cid == "g031" else []}
        p = {"case_id": cid, "question": "Synthetic question", "role": r.ROLES[cid], "plan_id": f"synthetic_plan_{cid}",
             "provider_model_contract": model, "raw_analyzer_response": canonical, "canonical_plan": canonical,
             "canonical_serialization": json.dumps(canonical, sort_keys=True), "contribution_ledger": ledger,
             "provenance_origin_receipts": [], "component_applicability_receipts": [{"component_value": r.COVERED, "applicability_status": "ACTIVE_IDENTIFIABLE"}] if cid == "g031" else [],
             "current_execution_projection": canonical, "treatment_execution_projection": canonical,
             "plan_signature": r.plan_signature(canonical), "provider_accounting": {**model, "analyzer_logical_calls": 1, "analyzer_provider_attempts": 1, "token_usage": 1},
             "matched_rule_identities": matched, "persistence_state": "RETRIEVAL_ELIGIBLE",
             "persisted_at": "2000-01-01T00:00:00Z", "gated_at": "2000-01-01T00:00:01Z", "treatment_execution_projection_diff_receipts": diff}
        plans.append(p)
        for arm in r.ARMS:
            slots.append({"cell_index": len(slots) + 1, "cell_id": f"{cid}_{arm}", "case_id": cid, "arm": arm,
                "status": "COMPLETED", "role": p["role"], "question": p["question"], "canonical_plan_id": p["plan_id"], "canonical_plan_signature": p["plan_signature"],
                "frozen_canonical_plan": canonical, "arm_execution_projection": canonical, "actual_plan_used": canonical,
                "plan_equality_arm_projection_verified": True, "final_evidence_object_ids": [oid], "evidence_items": [copy.deepcopy(item)],
                "provider_accounting": {"embedding_calls": 1, "generation_calls": 1, "model_calls": 2, "token_usage": 2}})
    historical = {"analyzer_calls": 4, "analyzer_provider_attempts": 4, "embedding_calls": 8, "reranker_calls": 8,
                  "token_usage": 20, **{k: 0 for k in r.ZERO_FIELDS}}
    return copy.deepcopy(({"plans": plans, "plans_planned": 4, "plans_recorded": 4, "plans_completed": 4, "accounting": {"analyzer_calls": 4, "analyzer_provider_attempts": 4, "token_usage": 4}},
        {"slots": slots, "slots_planned": 8, "slots_completed": 8, "accounting": {"embedding_calls": 8, "reranker_calls": 8, "model_calls": 16, "token_usage": 16}},
        gold, lookup, authority, historical, {"passed": True}))


def drop_evidence(bundle, index):
    bundle[1]["slots"][index]["final_evidence_object_ids"] = []
    bundle[1]["slots"][index]["evidence_items"] = []


def add_evidence(bundle, index, oid="synthetic.extra", resolved=True):
    item = {"object_id": oid, "source_id": "synthetic_source", "source_version_id": "synthetic_v1", "locator": {}}
    bundle[1]["slots"][index]["final_evidence_object_ids"].append(oid)
    bundle[1]["slots"][index]["evidence_items"].append(item)
    if resolved:
        bundle[3][oid] = copy.deepcopy(item)


def test_real_root_guard_rejection_only():
    r.assert_prefreeze_rejected(r.ROOT)


def test_synthetic_works_without_repository(tmp_path, monkeypatch, bundle):
    monkeypatch.chdir(tmp_path)
    result = r.audit_synthetic_fixture(*bundle)
    assert result["verification_status"] == "PASS"
    assert result["scientific_verdict_level"] == 6


@pytest.mark.parametrize("level", [1, 2, 3, 4, 5, 6])
def test_all_six_outcomes(bundle, level):
    if level == 1:
        bundle[0]["plans"].pop()
    elif level == 2:
        drop_evidence(bundle, 0)
    elif level == 3:
        drop_evidence(bundle, 1)
    elif level == 4:
        drop_evidence(bundle, 3)
    elif level == 5:
        bundle[0]["plans"][0]["component_applicability_receipts"][0]["applicability_status"] = "INACTIVE_NOT_IDENTIFIABLE"
    result = r.audit_synthetic_fixture(*bundle)
    assert result["scientific_verdict_level"] == level
    assert result["verification_status"] == ("FAIL" if level == 1 else "PASS")
    assert result["component_dispositions"][r.HOLD[0]] == "HOLD_DIRECT_TREATMENT_COVERAGE_GAP"
    assert result["component_dispositions"]["pflueger_2017:[51,57,65]"] == "HOLD_OUTSIDE_TREATMENT_SCOPE"


@pytest.mark.parametrize("field", ["raw_analyzer_response", "canonical_serialization", "provenance_origin_receipts", "provider_model_contract"])
def test_missing_plan_field_fails(bundle, field):
    del bundle[0]["plans"][0][field]
    assert r.audit_synthetic_fixture(*bundle)["scientific_verdict_level"] == 1


@pytest.mark.parametrize("mutation", ["timestamp", "state", "signature", "shared", "schedule", "projection", "provider", "ninth", "duplicate_plan", "origin", "independent", "control", "mask"])
def test_integrity_mutations_propagate(bundle, mutation):
    p, slots = bundle[0]["plans"][0], bundle[1]["slots"]
    if mutation == "timestamp": p["persisted_at"] = "2001-01-01T00:00:00Z"
    elif mutation == "state": p["persistence_state"] = "GATED"
    elif mutation == "signature": p["plan_signature"] = "wrong"
    elif mutation == "shared": slots[1]["frozen_canonical_plan"] = {}
    elif mutation == "schedule": slots.reverse()
    elif mutation == "projection": slots[0]["actual_plan_used"] = {}
    elif mutation == "provider": slots[0]["provider_accounting"]["embedding_calls"] = 2
    elif mutation == "ninth": slots.append(copy.deepcopy(slots[0]))
    elif mutation == "duplicate_plan": bundle[0]["plans"][1] = copy.deepcopy(p)
    elif mutation == "origin": p["treatment_execution_projection_diff_receipts"]["removed_rule_origin_entries"] = []
    elif mutation == "independent": p["contribution_ledger"][0]["provenance_origin_ids"] = [r.TARGET]
    elif mutation == "control": bundle[0]["plans"][1]["treatment_execution_projection"] = {"mutated": True}
    elif mutation == "mask": bundle[4]["covered_symbol_mask"] = []
    result = r.audit_synthetic_fixture(*bundle)
    assert result["verification_status"] == "FAIL"
    assert result["scientific_verdict_level"] == 1


@pytest.mark.parametrize("category", r.ZERO_FIELDS)
def test_historical_accounting_nonzero_fails(bundle, category):
    bundle[5][category] = 1
    assert r.audit_synthetic_fixture(*bundle)["verification_status"] == "FAIL"


@pytest.mark.parametrize("version", [None, "disallowed"])
def test_version_violation(bundle, version):
    bundle[1]["slots"][3]["evidence_items"][0]["source_version_id"] = version
    result = r.audit_synthetic_fixture(*bundle)
    assert result["scientific_verdict_level"] == 4
    receipt = result["version_safety"]["g032"][r.ARMS[1]]
    assert receipt["missing_invalid"] + receipt["violations"] == 1


@pytest.mark.parametrize("current,treatment,level", [(True, True, 6), (True, False, 6), (False, True, 4)])
def test_symmetric_unresolved(bundle, current, treatment, level):
    if current: add_evidence(bundle, 2, resolved=False)
    if treatment: add_evidence(bundle, 3, resolved=False)
    result = r.audit_synthetic_fixture(*bundle)
    assert result["scientific_verdict_level"] == level
    assert len(result["grounding_safety"]["g032"]["treatment_only_regressions"]) == int(level == 4)


def test_treatment_only_forbidden(bundle):
    add_evidence(bundle, 3)
    bundle[2]["g032"].forbidden_evidence = [GoldEvidenceSelector(object_id="synthetic.extra")]
    assert r.audit_synthetic_fixture(*bundle)["scientific_verdict_level"] == 4


def test_noncritical_variance_diagnostic_only(bundle):
    add_evidence(bundle, 3)
    result = r.audit_synthetic_fixture(*bundle)
    assert result["scientific_verdict_level"] == 6
    assert result["diagnostic_noncritical_variance"]["g032"]["noncritical_additions"] == ["synthetic.extra"]


@pytest.mark.parametrize("defect", ["parent", "message", "missing", "extra"])
def test_topology_rejects(defect):
    records = [{"head": "freeze", "parents": [r.INCIDENT], "message": r.FREEZE_MESSAGE},
               {"head": "close", "parents": ["freeze"], "message": r.CLOSE_MESSAGE}]
    if defect == "parent": records[0]["parents"] = ["wrong"]
    elif defect == "message": records[1]["message"] = "wrong"
    elif defect == "missing": records.pop()
    else: records.append(records[-1])
    assert r.validate_topology(records, final=True)


def test_blob_drift_rejected():
    assert r.compare_seal({"authority_blob": "a", "observed_blobs": {"HEAD": "a", "working": "a"}})
    assert not r.compare_seal({"authority_blob": "a", "observed_blobs": {"HEAD": "b"}})


@pytest.mark.parametrize("defect", [None, "parent", "message", "six_paths", "semantic_blob"])
def test_freeze_guard_mocked_metadata(tmp_path, monkeypatch, defect):
    def fake_git(root, *args):
        if args[0] == "rev-list": return "synthetic_freeze"
        if args[0] == "show":
            if args[-1] == r.INCIDENT:
                return r.A9 if args[2] == "--format=%P" else "D4-A9-R2-Fail"
            if args[2] == "--format=%P": return "wrong" if defect == "parent" else r.INCIDENT
            return "wrong" if defect == "message" else r.FREEZE_MESSAGE
        if args[0] == "diff": return "wrong" if defect == "six_paths" else "\n".join(sorted(set(r.PATHS) - {r.RESULT}))
        if args[0] == "hash-object": return "wrong" if defect == "semantic_blob" else "synthetic_blob"
        return "synthetic_blob"
    monkeypatch.setattr(r, "git", fake_git)
    if defect:
        with pytest.raises(r.VerifierNotFrozenError):
            r.require_verifier_freeze_checkpoint(tmp_path)
    else:
        assert r.require_verifier_freeze_checkpoint(tmp_path) == "synthetic_freeze"


def test_entire_result_including_safety_must_match(bundle):
    fresh = r.audit_synthetic_fixture(*bundle)
    committed = copy.deepcopy(fresh)
    assert r.compare_result_core(committed, fresh) == []
    committed["grounding_safety"]["g031"]["treatment_only_regressions"] = ["tampered"]
    assert r.compare_result_core(committed, fresh) == ["D4_A9_R2_MACHINE_RESULT_DRIFT"]


def test_protocol_precedes_missing_baseline(bundle):
    drop_evidence(bundle, 0)
    bundle[1]["slots"][7]["provider_accounting"]["generation_calls"] = 2
    assert r.audit_synthetic_fixture(*bundle)["scientific_verdict_level"] == 1


def test_required_source_type_regression(bundle):
    bundle[2]["g032"].required_source_types = ["paper"]
    for index in [2, 3]:
        add_evidence(bundle, index, oid="synthetic.paper")
    bundle[3]["synthetic.paper"]["source_id"] = "pflueger_2017"
    for index in [2, 3]:
        bundle[1]["slots"][index]["evidence_items"][-1]["source_id"] = "pflueger_2017"
    assert r.audit_synthetic_fixture(*bundle)["scientific_verdict_level"] == 6
    bundle[1]["slots"][3]["evidence_items"].pop()
    bundle[1]["slots"][3]["final_evidence_object_ids"].pop()
    assert r.audit_synthetic_fixture(*bundle)["scientific_verdict_level"] == 4


@pytest.mark.parametrize("saved_first", [True, False])
def test_frozen_executor_program_order_on_synthetic_source(saved_first):
    save = "        _save_json(raw_plans_path, record)\n"
    gate = "        if cid == 'g031':\n            raise RuntimeError()\n"
    source = "def execute_phase_p():\n    for cid in cases:\n" + (save + gate if saved_first else gate + save)
    source += "def execute_phase_r():\n    def _forbidden_analyze():\n        raise RuntimeError()\n    retriever.analyze = _forbidden_analyze\n"
    assert r.persistence_program_order(source)["passed"] is saved_first


@pytest.mark.parametrize("count", [6, 8])
def test_exact_path_gate(count, monkeypatch):
    monkeypatch.setattr(r, "git", lambda *args: "\n".join([str(i) for i in range(count)]))
    assert not r.valid_paths(r.changed_paths(Path("synthetic"), "before", "after"))


def test_static_isolation_accepts_this_module():
    test_module_path = Path(__file__)
    assert r.static_test_isolation(test_module_path.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("source", ["r." + "run_live_audit(root)", "r." + "verify_committed_closeout(root)",
    "f = r." + "run_live_audit", "x = Path('data').read_text()", "x = " + "RAW_PLANS_PATH", "x = eval('1')"])
def test_static_isolation_rejects_unsafe_tests(source):
    assert r.static_test_isolation(source)
