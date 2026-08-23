from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


def load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


capture = load("c7_a2_capture", "evaluation/scripts/capture_c7_a2_post_reranker.py")
evaluator = load("c7_a3_evaluator", "evaluation/scripts/evaluate_c7_a3_frozen_selectors.py")


def payload(object_id: str, source: str = "repo") -> dict:
    return {"object_id": object_id, "source_id": source, "source_version_id": "v1", "object_type": "source_file", "text": object_id, "locator": {"path": object_id + ".py"}, "authority_level": "primary"}


def rows() -> list[dict]:
    groups = {
        "installation": ("g001", "g002", "g003", "g004", "g005", "g006"),
        "usage": ("g010", "g013", "g014", "g015", "g017", "g019"),
        "algorithm_theory": ("g027", "g028", "g029", "g030", "g031"),
        "api": ("g044", "g047", "g050", "g051", "g052"),
        "troubleshooting": ("g059", "g060", "g105", "g114", "g115"),
        "algorithm_implementation": ("g110", "g112"), "module_structure": ("g113",),
    }
    intents = {case_id: intent for intent, case_ids in groups.items() for case_id in case_ids}
    return [{"case_id": case_id, "question": case_id, "intent": intents[case_id], "retrieval_plan": {"intent": intents[case_id], "source_budgets": {"code": 1.0}}} for case_id in capture.EXPECTED_PARENT_IDS]


def selector(ordered, payloads, scores, channels, plan, limit, mandatory):
    return ([{"object_id": oid} for oid in ordered[:limit]], [{"object_id": "x", "reason": "fixture"}], [{"object_id": "y", "reason": "fixture"}])


def passing_preregistration() -> dict:
    prereg = capture.build_preregistration(
        capture.EXPECTED_PARENT_IDS,
        rows(),
        source_head=capture.EXPECTED_HEAD,
        plan_factory=lambda value: value,
    )
    prereg["a2_verdict"] = "PASS"
    prereg["a3_eligibility"] = "NEXT_ELIGIBLE / NOT_STARTED"
    return prereg


def record(case_id="g001") -> dict:
    integrity = {"frozen_plan_used": True, "analyzer_called": False, "production_selector_spy_captured": True, "stage_p_complete": True, "payload_universe_complete": True, "score_map_complete": True, "channel_map_complete": True, "exact_stream_complete": True, "external_reads_required_for_future_replay": False, "s0_selected_parity": True, "s0_excluded_parity": True, "s0_backfill_parity": True}
    return {"schema_version": "c7-a2-post-reranker-capture-v1", "source_head": capture.EXPECTED_HEAD, "implementation_identity": {"source_index_identity": "fixture"}, "case_id": case_id, "question": case_id, "frozen_plan": {"intent": "usage", "source_budgets": {"code": 1.0}}, "channel_rankings": {"exact": ["a"], "dense": ["b"]}, "stage_f_order": ["a", "b"], "stage_f_scores": {"a": 2 / 61, "b": 1 / 61}, "stage_r_order": ["b"], "stage_r_stage_f_ranks": [{"object_id": "b", "stage_f_rank": 2}], "reranker_pool_ids": ["a", "b"], "stage_m_order": ["b", "a"], "stage_p_order": ["a", "b"], "candidate_payloads": {"a": payload("a"), "b": payload("b", "other")}, "retrieval_channels": {"a": ["exact"], "b": ["dense"]}, "exact_stream_order": ["a"], "mandatory_symbol_ids": [], "final_evidence_limit": 2, "current_s0": {"selected_object_ids": ["a", "b"], "excluded": [{"object_id": "x", "reason": "fixture"}], "backfill_admissions": [{"object_id": "y", "reason": "fixture"}]}, "capture_integrity": integrity}


class CaptureTests(unittest.TestCase):
    def test_preregistration_exact_cohort_and_duplicate_missing_fail(self) -> None:
        prereg = capture.build_preregistration(capture.EXPECTED_PARENT_IDS, rows(), source_head=capture.EXPECTED_HEAD, plan_factory=lambda value: value)
        self.assertEqual(prereg["frozen_cohort_case_ids"], list(capture.EXPECTED_COHORT_IDS))
        self.assertEqual(prereg["cohort_intent_counts"], capture.EXPECTED_COHORT_INTENT_COUNTS)
        with self.assertRaises(ValueError): capture.build_preregistration(capture.EXPECTED_PARENT_IDS, rows()[:-1], source_head=capture.EXPECTED_HEAD, plan_factory=lambda value: value)
        with self.assertRaises(ValueError): capture.build_preregistration(capture.EXPECTED_PARENT_IDS, rows() + [rows()[0]], source_head=capture.EXPECTED_HEAD, plan_factory=lambda value: value)

    def test_cli_is_mutually_exclusive_and_fail_closed(self) -> None:
        with self.assertRaises(SystemExit): capture.main([])
        parser_source = (ROOT / "evaluation/scripts/capture_c7_a2_post_reranker.py").read_text(encoding="utf-8")
        self.assertIn("add_mutually_exclusive_group(required=True)", parser_source)
        self.assertNotIn("--execute-live requires the authorized host", parser_source)

    def test_prepare_writes_temp_preregistration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "preregistration.json"
            with mock.patch.object(capture, "production_plan", side_effect=lambda row, plan_factory=None: row["retrieval_plan"]):
                result = capture.prepare_artifact(output, parent_ids=capture.EXPECTED_PARENT_IDS, replay_rows=rows(), source_head=capture.EXPECTED_HEAD)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["frozen_cohort_case_ids"], list(capture.EXPECTED_COHORT_IDS))
            self.assertIn("supported_precision", result["secondary_metrics"])
            self.assertEqual(len(result["hard_gates"]), 12)

    def test_stage_f_ties_and_m(self) -> None:
        order, scores = capture.reconstruct_stage_f({"exact": ["a"], "dense": ["b"], "sparse": ["b", "a"]})
        self.assertEqual(order, ["a", "b"]); self.assertAlmostEqual(scores["a"], 2 / 61 + 1 / 62)
        self.assertEqual(capture.reconstruct_stage_m(["b", "a"], ["a", "c"]), ["b", "a", "c"])

    def test_spy_complete_restored_and_live_scores_ranks(self) -> None:
        module = SimpleNamespace(select_final_evidence=selector)
        class Retriever:
            def retrieve(self, question, plan):
                scores = {"a": 2 / 61, "b": 1 / 61}
                module.select_final_evidence(["a", "b"], {"a": payload("a"), "b": payload("b")}, scores, {"a": ["exact"], "b": ["dense"]}, plan, 2, set())
                return {"rankings": {"exact": [payload("a")], "dense": [payload("b")]}, "fusion_scores": scores, "reranked_object_ids": ["b"]}
        original = module.select_final_evidence
        result = capture.execute_live(Retriever(), case_id="g001", question="q", frozen_plan={"intent": "usage"}, source_head=capture.EXPECTED_HEAD, selector_module=module, replay_dependencies={"selector": selector, "plan_factory": lambda value: value})
        self.assertIs(module.select_final_evidence, original)
        self.assertEqual(result["stage_f_scores"], {"a": 2 / 61, "b": 1 / 61})
        self.assertEqual(result["channel_rankings"], {"exact": ["a"], "dense": ["b"], "sparse": [], "paper": [], "workflow": [], "graph": []})
        self.assertEqual(result["stage_r_stage_f_ranks"], [{"object_id": "b", "stage_f_rank": 2}])
        self.assertTrue(all(value for key, value in result["capture_integrity"].items() if key not in {"analyzer_called", "external_reads_required_for_future_replay"}), result["capture_integrity"])
        self.assertFalse(result["capture_integrity"]["analyzer_called"])
        self.assertFalse(result["capture_integrity"]["external_reads_required_for_future_replay"])

    def test_recursive_forbidden_and_offline_parity(self) -> None:
        dependencies = {"selector": selector, "plan_factory": lambda value: value}
        self.assertEqual(capture.validate_record(record(), **dependencies), {"selected": True, "excluded": True, "backfill": True})
        invalid = copy.deepcopy(record()); invalid["nested"] = {"gold": ["x"]}
        with self.assertRaises(ValueError): capture.validate_record(invalid, **dependencies)

    def test_complete_bundle_and_single_attempt_failure_ledger(self) -> None:
        prereg = capture.build_preregistration(capture.EXPECTED_PARENT_IDS, rows(), source_head=capture.EXPECTED_HEAD, plan_factory=lambda value: value)
        prereg["capture_call_ledger"] = {"retrieval_calls": 18, "reranker_calls": 18, "analyzer_calls": 0, "gold_evaluations": 0, "s1_real_cohort_calls": 0, "qa_calls": 0, "verifier_calls": 0, "judge_calls": 0}
        records = [record(case_id) for case_id in capture.EXPECTED_COHORT_IDS]
        dependencies = {"selector": selector, "plan_factory": lambda value: value}
        self.assertEqual(capture.validate_capture_bundle(prereg, records, **dependencies)["s0_replay_parity"], "18/18")
        calls = []
        def fake_execute(_retriever, *, case_id, **kwargs):
            calls.append(case_id)
            _retriever.vertex.generate_json()
            if case_id == capture.EXPECTED_COHORT_IDS[2]: raise RuntimeError("fixture failure")
            return {"case_id": case_id}
        factories = []
        def factory():
            value = SimpleNamespace(analyze=lambda question: None, vertex=SimpleNamespace(generate_json=lambda: {})); factories.append(value); return value
        captured, ledger = capture.run_live_capture(prereg, {row["case_id"]: row for row in rows()}, factory, source_head=capture.EXPECTED_HEAD, execute_one=fake_execute, plan_factory=lambda value: value)
        self.assertEqual(calls, list(capture.EXPECTED_COHORT_IDS)); self.assertEqual(ledger["retrieval_calls"], 18)
        self.assertEqual(ledger["reranker_calls"], 18); self.assertEqual(ledger["analyzer_calls"], 0)
        self.assertEqual(len(factories), 1)
        self.assertEqual(prereg["capture_call_ledger"], ledger)
        failed = captured[2]; self.assertTrue(failed["single_attempt"]); self.assertIsNone(failed["replacement_case_id"])
        self.assertEqual(capture.validate_capture_bundle(prereg, captured)["status"], "CAPTURE_INCOMPLETE/INCONCLUSIVE")
        with tempfile.TemporaryDirectory() as directory:
            manifest, jsonl = Path(directory) / "manifest.json", Path(directory) / "capture.jsonl"
            manifest.write_text(json.dumps(prereg), encoding="utf-8")
            jsonl.write_text("".join(json.dumps(item) + "\n" for item in records), encoding="utf-8")
            self.assertEqual(capture.validate_artifacts(manifest, jsonl, **dependencies)["status"], "PASS")
        bad_ledger = copy.deepcopy(prereg); bad_ledger["capture_call_ledger"]["reranker_calls"] = 17
        with self.assertRaises(ValueError): capture.validate_capture_bundle(bad_ledger, records, **dependencies)
        bad_integrity = copy.deepcopy(records); bad_integrity[0]["capture_integrity"]["score_map_complete"] = False
        with self.assertRaises(ValueError): capture.validate_capture_bundle(prereg, bad_integrity, **dependencies)

    def test_evaluator_metrics_gates_and_role_decision(self) -> None:
        base = {"input_identity": "same", "upstream_calls": {"retrieval": False, "reranker": False, "analyzer": False, "db": False}, "final_evidence_recall": 1, "new_critical_misses": 0, "new_protected_losses": 0, "explicit_required_satisfaction": 1, "new_required_misses": 0, "selector_displacement": 0, "version_source_violations": 0, "forced_irrelevant": 0, "deterministic": True, "preferred_invariant": True, "no_benchmark_specific_rule": True, "preregistration_intact": True}
        gates = evaluator.gate_matrix(base, base); self.assertEqual(set(gates), set(evaluator.GATE_NAMES)); self.assertEqual(gates["forced_irrelevant_evidence"], evaluator.NOT_SUPPORTED)
        metrics = {name: 1.0 for name in evaluator.PRIMARY_METRICS}; metrics["selector_caused_relevant_displacement"] = 0.0
        self.assertEqual(evaluator.meaningful_gain(metrics, metrics, gates), "NO_MEANINGFUL_GAIN/INCONCLUSIVE")
        bad = dict(gates, final_evidence_recall="FAIL")
        improved = dict(metrics, final_evidence_recall=1.1)
        self.assertEqual(evaluator.meaningful_gain(metrics, improved, bad), "CURRENT_PREFERRED_GATE_FAILURE")
        displacement = evaluator.selector_displacement([], {"relevant_groups_by_object": {"a": ["g"]}}, [{"object_id": "a", "decision_reason": "maximum"}], ["a"])
        self.assertEqual(displacement["receipts"][0]["candidate_reasons"]["a"], "maximum")

    def test_full_offline_same_input_evaluator_fixture(self) -> None:
        frozen = record()
        s0 = lambda _record: {"selected_object_ids": ["a", "b"]}
        s1 = lambda _record: {"selected_object_ids": ["a"], "candidate_receipts": [{"object_id": "b", "decision_reason": "maximum"}], "constraint_receipts": []}
        annotations = {"relevant_groups": ["group-a"], "critical_groups": [], "relevant_groups_by_object": {"a": ["group-a"]}, "critical_groups_by_object": {}}
        result = evaluator.evaluate_frozen_case(frozen, annotations, s0_runner=s0, s1_runner=s1)
        self.assertEqual(set(result["s0"]["metrics"]), set(evaluator.PRIMARY_METRICS))
        self.assertTrue({"evidence_counts", "supported_precision", "source_concentration", "constraint_decision_counts", "graph_exposure", "workflow_exposure", "first_relevant_rank"} <= set(result["secondary"]))
        self.assertEqual(result["input_identity"]["stage_f"], frozen["stage_f_order"])
        self.assertEqual(result["secondary"]["displacement_reasons"]["s1"]["count"], 0)
        cohort = evaluator.evaluate_frozen_cohort([frozen], {"g001": annotations}, s0_runner=s0, s1_runner=s1, preregistration=passing_preregistration())
        self.assertEqual(set(cohort["gates"]), set(evaluator.GATE_NAMES))

    def test_gate_9_supported_failure_and_not_supported(self) -> None:
        frozen = record()
        frozen["final_evidence_limit"] = 1
        s0 = lambda _record: {"selected_object_ids": ["a"], "candidate_receipts": [{"object_id": "b", "decision_reason": "final_evidence_limit"}]}
        s1 = lambda _record: {"selected_object_ids": ["b"], "candidate_receipts": [{"object_id": "a", "decision_reason": "maximum"}, {"object_id": "b", "decision_reason": "required_override", "required_override": True}], "constraint_receipts": []}
        annotations = {"relevant_groups": ["group-a"], "critical_groups": [], "relevant_groups_by_object": {"a": ["group-a"]}, "critical_groups_by_object": {}, "negative_completeness": True, "known_irrelevant_object_ids": ["b"]}
        result = evaluator.evaluate_frozen_cohort([frozen], {"g001": annotations}, s0_runner=s0, s1_runner=s1, preregistration=passing_preregistration())
        self.assertEqual(result["aggregate"]["forced_irrelevant_evidence"], {"status": "SUPPORTED", "count": 1})
        self.assertEqual(result["gates"]["forced_irrelevant_evidence"], "FAIL")
        unsupported = copy.deepcopy(annotations)
        unsupported.pop("negative_completeness")
        result = evaluator.evaluate_frozen_cohort([frozen], {"g001": unsupported}, s0_runner=s0, s1_runner=s1, preregistration=passing_preregistration())
        self.assertEqual(result["gates"]["forced_irrelevant_evidence"], evaluator.NOT_SUPPORTED)

    def test_gate_11_and_12_are_static_evidence_not_caller_booleans(self) -> None:
        prereg = passing_preregistration()
        proof = evaluator.static_s1_contract_proof(prereg)
        self.assertTrue(proof["passed"], proof)
        broken = copy.deepcopy(prereg)
        broken["s1_identity"] = "case-specific-policy"
        self.assertFalse(evaluator.static_s1_contract_proof(broken)["passed"])
        self.assertFalse(evaluator.preregistration_integrity(broken)["passed"])

    def test_capture_has_no_shadow_or_outcome_execution_and_production_isolation(self) -> None:
        source = (ROOT / "evaluation/scripts/capture_c7_a2_post_reranker.py").read_text(encoding="utf-8")
        self.assertNotIn("shadow_select", source); self.assertNotIn("gold_questions", source)
        import subprocess
        self.assertEqual(subprocess.run(["git", "diff", "--name-only", "--", "src", "configs"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip(), "")


if __name__ == "__main__": unittest.main()
