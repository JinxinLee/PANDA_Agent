from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any
import unittest

from panda_agent.evidence_selection import (
    ConstraintDimension,
    ConstraintType,
    FrozenShadowInput,
    POLICY_ID,
    SelectionConstraint,
    ShadowSelectionPolicy,
    _source_type_of,
    shadow_select,
    stage_m_merge,
    translate_current_policy,
)


def _payload(object_id: str, source_id: str = "repository", path: str | None = None,
             object_type: str = "source_file") -> dict:
    return {
        "object_id": object_id,
        "source_id": source_id,
        "object_type": object_type,
        "locator": {"path": path if path is not None else f"src/{object_id}.py"},
    }


def _input(*object_ids: str, plan: dict | None = None, payloads: dict | None = None,
           channels: dict | None = None, mandatory: frozenset[str] = frozenset(),
           stage_f: tuple[str, ...] = ()) -> FrozenShadowInput:
    payloads = payloads or {object_id: _payload(object_id) for object_id in object_ids}
    channels = channels or {object_id: ("dense",) for object_id in object_ids}
    return FrozenShadowInput(
        plan=plan or {"source_budgets": {"code": 1.0}},
        stage_r_order=tuple(object_ids), stage_f_order=stage_f,
        payloads=payloads, retrieval_channels=channels, mandatory_symbol_ids=mandatory,
    )


def _constraint(kind: ConstraintType, dimension: ConstraintDimension, value: str,
                identity: str, limit: int | None = None) -> SelectionConstraint:
    return SelectionConstraint(identity, kind, dimension, value, "fixture", "fixture", limit)


class EvidenceSelectionSmokeTests(unittest.TestCase):
    def test_stage_m_is_reranker_order_then_fusion_fallback(self) -> None:
        self.assertEqual(stage_m_merge(["r2", "r1"], ["r1", "f1", "f2"]), ["r2", "r1", "f1", "f2"])

    def test_shadow_selector_is_plain_data_only(self) -> None:
        frozen = FrozenShadowInput(
            plan={"source_budgets": {"code": 1.0}},
            stage_r_order=("one",), stage_f_order=(),
            payloads={"one": {"object_id": "one", "source_id": "repo", "object_type": "source_file", "locator": {"path": "src/a.py"}}},
            retrieval_channels={"one": ("dense",)},
        )
        self.assertEqual(shadow_select(frozen).selected_object_ids, ["one"])


class ExplicitSelectionContractTests(unittest.TestCase):
    def test_dimensions_keep_graph_as_channel_and_workflow_separate(self) -> None:
        policy = translate_current_policy({
            "source_budgets": {"graph": 0.3, "workflow": 0.7},
            "required_source_types": ["graph", "workflow"],
        })
        pairs = {(c.constraint_type, c.dimension, c.value) for c in policy.constraints}
        self.assertNotIn((ConstraintType.MAXIMUM, ConstraintDimension.SOURCE_TYPE, "graph"), pairs)
        self.assertIn((ConstraintType.MAXIMUM, ConstraintDimension.RETRIEVAL_CHANNEL, "graph"), pairs)
        self.assertIn((ConstraintType.PREFERRED, ConstraintDimension.RETRIEVAL_CHANNEL, "graph"), pairs)
        self.assertIn((ConstraintType.PREFERRED, ConstraintDimension.SOURCE_TYPE, "workflow"), pairs)
        self.assertIn((ConstraintType.PREFERRED, ConstraintDimension.RETRIEVAL_CHANNEL, "workflow"), pairs)

    def test_source_budgets_become_source_type_maximums(self) -> None:
        policy = translate_current_policy({"source_budgets": {"code": 0.25, "documentation": 0.75}}, 12)
        caps = {(c.value, c.limit) for c in policy.constraints if c.constraint_type is ConstraintType.MAXIMUM and c.dimension is ConstraintDimension.SOURCE_TYPE}
        self.assertEqual(caps, {("code", 3), ("documentation", 9)})

    def test_static_intent_defaults_are_preferred_not_required(self) -> None:
        policy = translate_current_policy({"source_budgets": {"code": 1.0}, "required_source_types": ["code"]})
        defaults = [c for c in policy.constraints if c.value == "code" and c.provenance == "reviewed_static_intent_policy"]
        self.assertEqual([c.constraint_type for c in defaults], [ConstraintType.PREFERRED])
        self.assertTrue(defaults[0].not_question_required)

    def test_required_is_generated_only_from_exact_explicit_parse_provenance(self) -> None:
        plan = {
            "source_budgets": {"code": 1.0}, "target_repositories": ["alpha", "beta"],
            "analysis_diagnostics": {"deterministic_parse": {"provenance": {"target_repositories": [
                {"source": "explicit_query_reference", "value": "alpha"},
                {"source": "legacy_query_rule", "value": "beta"},
                {"source": "explicit_query_reference", "value": "not-a-target"},
            ]}}},
        }
        required = [c.value for c in translate_current_policy(plan).constraints if c.constraint_type is ConstraintType.REQUIRED]
        self.assertEqual(required, ["alpha"])

    def test_protected_bypasses_source_and_type_maximum(self) -> None:
        plan = {"source_budgets": {"code": 0.25, "documentation": 0.75}}
        frozen = _input("protected-one", "protected-two", plan=plan, mandatory=frozenset({"protected-one", "protected-two"}))
        result = shadow_select(frozen, translate_current_policy(plan, 4, frozen.mandatory_symbol_ids))
        self.assertEqual(result.selected_object_ids, ["protected-one", "protected-two"])
        self.assertEqual(result.candidate_receipts[1]["decision_reason"], "protected_override")
        maximum = [r for r in result.constraint_receipts if r["constraint_type"] == "MAXIMUM" and r["matched_candidate_ids"]]
        self.assertTrue(all(r["status"] == "satisfied" for r in maximum))

    def test_protected_duplicate_is_still_rejected(self) -> None:
        payloads = {"first": _payload("first", path="same"), "second": _payload("second", path="same")}
        frozen = _input("first", "second", payloads=payloads, mandatory=frozenset({"first", "second"}))
        result = shadow_select(frozen)
        self.assertEqual(result.selected_object_ids, ["first"])
        self.assertEqual(result.candidate_receipts[1]["decision_reason"], "duplicate_locator")

    def test_protected_never_bypasses_final_limit(self) -> None:
        frozen = _input("first", "second", mandatory=frozenset({"first", "second"}))
        result = shadow_select(frozen, translate_current_policy(frozen.plan, 1, frozen.mandatory_symbol_ids))
        self.assertEqual(result.selected_object_ids, ["first"])
        self.assertEqual(result.candidate_receipts[1]["decision_reason"], "final_evidence_limit")

    def test_preferred_never_forces_fill_or_backfill(self) -> None:
        plan = {"source_budgets": {"code": 1.0}, "required_source_types": ["documentation"]}
        result = shadow_select(_input("only", plan=plan), translate_current_policy(plan, 3))
        self.assertEqual(result.selected_object_ids, ["only"])
        preferred = next(r for r in result.constraint_receipts if r["constraint_type"] == "PREFERRED")
        self.assertEqual(preferred["status"], "not_applicable")

    def test_matching_preferred_candidate_cannot_bypass_maximum(self) -> None:
        plan = {"source_budgets": {"code": 0.25, "documentation": 0.75}, "required_source_types": ["code"]}
        payloads = {"first": _payload("first", "one"), "second": _payload("second", "two")}
        result = shadow_select(_input("first", "second", plan=plan, payloads=payloads), translate_current_policy(plan, 4))
        self.assertEqual(result.selected_object_ids, ["first"])
        excluded = result.candidate_receipts[1]
        self.assertEqual(excluded["decision_reason"], "maximum")
        self.assertNotIn("preferred", excluded["priority_reasons"])
        self.assertTrue(excluded["preferred_match_without_admission_effect"])
        self.assertEqual(excluded["admission_phase"], "stage_s")
        preferred = next(r for r in result.constraint_receipts if r["constraint_type"] == "PREFERRED")
        self.assertFalse(preferred["admission_effect"])

    def test_preferred_does_not_change_admission_membership(self) -> None:
        object_ids = tuple(f"rank-{rank:02d}" for rank in range(1, 51))
        frozen = _input(*object_ids)
        preferred = _constraint(
            ConstraintType.PREFERRED, ConstraintDimension.OBJECT_ID,
            "rank-50", "preferred-rank-50",
        )
        without_preferred = shadow_select(
            frozen, ShadowSelectionPolicy(POLICY_ID, 12, ()),
        )
        with_preferred = shadow_select(
            frozen, ShadowSelectionPolicy(POLICY_ID, 12, (preferred,)),
        )
        expected = {f"rank-{rank:02d}" for rank in range(1, 13)}
        self.assertEqual(set(without_preferred.selected_object_ids), expected)
        self.assertEqual(set(with_preferred.selected_object_ids), expected)
        preferred_candidate = next(
            receipt for receipt in with_preferred.candidate_receipts
            if receipt["object_id"] == "rank-50"
        )
        self.assertTrue(preferred_candidate["preferred_match_without_admission_effect"])
        self.assertEqual(preferred_candidate["decision_reason"], "final_evidence_limit")

    def test_required_eligible_candidate_is_selected_and_receipted(self) -> None:
        plan = {"source_budgets": {"code": 1.0}, "target_repositories": ["alpha"],
                "analysis_diagnostics": {"deterministic_parse": {"provenance": {"target_repositories": [
                    {"source": "explicit_query_reference", "value": "alpha"}]}}}}
        payloads = {"ordinary": _payload("ordinary", "other"), "required": _payload("required", "alpha")}
        result = shadow_select(_input("ordinary", "required", plan=plan, payloads=payloads))
        self.assertEqual(result.selected_object_ids[0], "required")
        receipt = next(r for r in result.constraint_receipts if r["constraint_type"] == "REQUIRED")
        self.assertEqual(receipt["status"], "satisfied")
        self.assertEqual(receipt["selected_candidate_ids"], ["required"])

    def test_required_promotes_only_minimum_deterministic_representative(self) -> None:
        required = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            "alpha", "required-alpha",
        )
        object_ids = ("ordinary-1", "ordinary-2", "required-1", "ordinary-3", "required-2")
        payloads = {
            object_id: _payload(
                object_id, "alpha" if object_id.startswith("required") else "other"
            )
            for object_id in object_ids
        }
        result = shadow_select(
            _input(*object_ids, payloads=payloads),
            ShadowSelectionPolicy(POLICY_ID, 3, (required,)),
        )
        self.assertEqual(
            result.stage_p_order,
            ["required-1", "ordinary-1", "ordinary-2", "ordinary-3", "required-2"],
        )
        self.assertEqual(result.selected_object_ids, ["required-1", "ordinary-1", "ordinary-2"])
        receipts = {receipt["object_id"]: receipt for receipt in result.candidate_receipts}
        self.assertTrue(receipts["required-1"]["required_representative"])
        self.assertFalse(receipts["required-2"]["required_representative"])
        constraint = result.constraint_receipts[0]
        self.assertEqual(constraint["eligible_candidate_ids"], ["required-1", "required-2"])
        self.assertEqual(constraint["satisfying_candidate_ids"], ["required-1"])

    def test_required_already_satisfied_does_not_promote_another_match(self) -> None:
        required = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            "alpha", "required-alpha",
        )
        payloads = {
            "required-1": _payload("required-1", "alpha"),
            "ordinary": _payload("ordinary", "other"),
            "required-2": _payload("required-2", "alpha"),
        }
        result = shadow_select(
            _input("required-1", "ordinary", "required-2", payloads=payloads),
            ShadowSelectionPolicy(POLICY_ID, 2, (required,)),
        )
        self.assertEqual(result.stage_p_order, ["required-1", "ordinary", "required-2"])
        self.assertEqual(result.selected_object_ids, ["required-1", "ordinary"])
        receipts = {receipt["object_id"]: receipt for receipt in result.candidate_receipts}
        self.assertTrue(receipts["required-1"]["required_representative"])
        self.assertFalse(receipts["required-2"]["required_representative"])

    def test_required_representative_can_override_maximum(self) -> None:
        maximum = _constraint(
            ConstraintType.MAXIMUM, ConstraintDimension.SOURCE_ID,
            "alpha", "maximum-alpha", limit=0,
        )
        required = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            "alpha", "required-alpha",
        )
        frozen = _input("required", payloads={"required": _payload("required", "alpha")})
        result = shadow_select(
            frozen, ShadowSelectionPolicy(POLICY_ID, 1, (maximum, required)),
        )
        self.assertEqual(result.selected_object_ids, ["required"])
        candidate = result.candidate_receipts[0]
        self.assertEqual(candidate["decision_reason"], "required_override")
        self.assertTrue(candidate["required_override"])
        required_receipt = next(
            receipt for receipt in result.constraint_receipts
            if receipt["constraint_type"] == "REQUIRED"
        )
        maximum_receipt = next(
            receipt for receipt in result.constraint_receipts
            if receipt["constraint_type"] == "MAXIMUM"
        )
        self.assertEqual(required_receipt["satisfying_candidate_ids"], ["required"])
        self.assertEqual(required_receipt["status"], "satisfied")
        self.assertEqual(maximum_receipt["status"], "satisfied")

    def test_invalid_or_unusable_match_cannot_satisfy_required(self) -> None:
        required = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            "alpha", "required-alpha",
        )
        payloads = {
            "invalid": _payload("invalid", "alpha"),
            "unusable": _payload("unusable", "alpha"),
            "ordinary": _payload("ordinary", "other"),
        }
        payloads["invalid"]["valid"] = False
        payloads["unusable"]["usable"] = False
        result = shadow_select(
            _input("invalid", "unusable", "ordinary", payloads=payloads),
            ShadowSelectionPolicy(POLICY_ID, 3, (required,)),
        )
        constraint = result.constraint_receipts[0]
        self.assertEqual(constraint["eligible_candidate_ids"], [])
        self.assertEqual(constraint["satisfying_candidate_ids"], [])
        self.assertEqual(constraint["status"], "unsatisfied")
        self.assertTrue(all(
            receipt["decision_reason"] == "invalid_candidate"
            for receipt in result.candidate_receipts[:2]
        ))

    def test_duplicate_match_cannot_be_required_representative(self) -> None:
        required = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            "alpha", "required-alpha",
        )
        payloads = {
            "survivor": _payload("survivor", "other", path="same"),
            "duplicate-required": _payload("duplicate-required", "alpha", path="same"),
        }
        result = shadow_select(
            _input("survivor", "duplicate-required", payloads=payloads),
            ShadowSelectionPolicy(POLICY_ID, 2, (required,)),
        )
        self.assertEqual(result.selected_object_ids, ["survivor"])
        self.assertFalse(result.candidate_receipts[1]["required_representative"])
        self.assertEqual(result.candidate_receipts[1]["decision_reason"], "duplicate_locator")
        self.assertEqual(result.constraint_receipts[0]["status"], "unsatisfied")

    def test_one_candidate_can_satisfy_multiple_required_constraints(self) -> None:
        required_source = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            "alpha", "required-alpha",
        )
        required_channel = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.RETRIEVAL_CHANNEL,
            "graph", "required-graph",
        )
        payloads = {
            "ordinary": _payload("ordinary", "other"),
            "both": _payload("both", "alpha"),
        }
        channels = {"ordinary": ("dense",), "both": ("dense", "graph")}
        result = shadow_select(
            _input("ordinary", "both", payloads=payloads, channels=channels),
            ShadowSelectionPolicy(POLICY_ID, 2, (required_source, required_channel)),
        )
        self.assertEqual(result.selected_object_ids.count("both"), 1)
        both = next(r for r in result.candidate_receipts if r["object_id"] == "both")
        self.assertEqual(
            both["satisfying_required_constraints"],
            ["required-alpha", "required-graph"],
        )
        self.assertTrue(all(
            receipt["satisfying_candidate_ids"] == ["both"]
            and receipt["status"] == "satisfied"
            for receipt in result.constraint_receipts
        ))

    def test_one_candidate_can_record_required_and_protected_roles(self) -> None:
        maximum = _constraint(
            ConstraintType.MAXIMUM, ConstraintDimension.SOURCE_ID,
            "alpha", "maximum-alpha", limit=0,
        )
        required = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            "alpha", "required-alpha",
        )
        protected = _constraint(
            ConstraintType.PROTECTED, ConstraintDimension.OBJECT_ID,
            "both", "protected-both",
        )
        result = shadow_select(
            _input("both", payloads={"both": _payload("both", "alpha")}),
            ShadowSelectionPolicy(POLICY_ID, 1, (maximum, required, protected)),
        )
        self.assertEqual(result.selected_object_ids, ["both"])
        candidate = result.candidate_receipts[0]
        self.assertTrue(candidate["required_representative"])
        self.assertTrue(candidate["required_override"])
        self.assertTrue(candidate["protected"])
        self.assertTrue(candidate["protected_override"])
        self.assertEqual(candidate["satisfying_required_constraints"], ["required-alpha"])

    def test_final_limit_reports_unsatisfied_required_without_overflow(self) -> None:
        required_alpha = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            "alpha", "required-alpha",
        )
        required_beta = _constraint(
            ConstraintType.REQUIRED, ConstraintDimension.SOURCE_ID,
            "beta", "required-beta",
        )
        payloads = {
            "alpha": _payload("alpha", "alpha"),
            "beta": _payload("beta", "beta"),
        }
        result = shadow_select(
            _input("alpha", "beta", payloads=payloads),
            ShadowSelectionPolicy(POLICY_ID, 1, (required_alpha, required_beta)),
        )
        self.assertEqual(result.selected_object_ids, ["alpha"])
        self.assertEqual(result.candidate_receipts[1]["decision_reason"], "final_evidence_limit")
        statuses = {
            receipt["constraint_id"]: receipt["status"]
            for receipt in result.constraint_receipts
        }
        self.assertEqual(statuses, {"required-alpha": "satisfied", "required-beta": "unsatisfied"})

    def test_required_without_candidate_is_unsatisfied_without_invention(self) -> None:
        plan = {"source_budgets": {"code": 1.0}, "target_repositories": ["alpha"],
                "analysis_diagnostics": {"deterministic_parse": {"provenance": {"target_repositories": [
                    {"source": "explicit_query_reference", "value": "alpha"}]}}}}
        result = shadow_select(_input("ordinary", plan=plan))
        receipt = next(r for r in result.constraint_receipts if r["constraint_type"] == "REQUIRED")
        self.assertEqual(receipt["status"], "unsatisfied")
        self.assertEqual(receipt["selected_candidate_ids"], [])

    def test_maximum_prevents_source_domination(self) -> None:
        payloads = {name: _payload(name, "same") for name in ("one", "two", "three")}
        result = shadow_select(_input("one", "two", "three", payloads=payloads), translate_current_policy({"source_budgets": {"code": 1.0}}, 4))
        self.assertEqual(result.selected_object_ids, ["one", "two"])
        self.assertEqual(result.candidate_receipts[2]["decision_reason"], "maximum")

    def test_empty_locator_uses_object_identity_and_duplicates_are_deterministic(self) -> None:
        payloads = {"one": _payload("one", path=""), "two": _payload("two", path="")}
        payloads["one"]["locator"] = {}
        payloads["two"]["locator"] = {}
        result = shadow_select(_input("one", "two", payloads=payloads))
        self.assertEqual(result.selected_object_ids, ["one", "two"])
        self.assertEqual([r["locator_identity"] for r in result.candidate_receipts], ["object:one", "object:two"])

    def test_ordinary_duplicate_locator_is_a_hard_exclusion(self) -> None:
        payloads = {"first": _payload("first", path="same"), "second": _payload("second", path="same")}
        result = shadow_select(_input("first", "second", payloads=payloads))
        self.assertEqual(result.selected_object_ids, ["first"])
        duplicate = result.candidate_receipts[1]
        self.assertEqual(duplicate["final_decision"], "EXCLUDED")
        self.assertEqual(duplicate["decision_reason"], "duplicate_locator")
        self.assertEqual(duplicate["duplicate_status"], "DUPLICATE")
        self.assertEqual(duplicate["blocking_constraint"], "duplicate_locator")

    def test_invalid_candidate_keeps_maximum_receipts_satisfied(self) -> None:
        payloads = {"invalid": _payload("invalid")}
        payloads["invalid"]["valid"] = False
        result = shadow_select(_input("invalid", payloads=payloads), translate_current_policy({"source_budgets": {"code": 1.0}}, 4))
        self.assertEqual(result.candidate_receipts[0]["decision_reason"], "invalid_candidate")
        maximum = [r for r in result.constraint_receipts if r["constraint_type"] == "MAXIMUM"]
        self.assertEqual(len(maximum), 2)
        self.assertTrue(all(r["status"] == "satisfied" for r in maximum))
        self.assertTrue(all(r["selected_candidate_ids"] == [] for r in maximum))

    def test_stage_p_and_full_receipts_are_stable(self) -> None:
        frozen = _input("one", "two", stage_f=("two", "three"), payloads={
            "one": _payload("one", "ordinary"), "two": _payload("two", "alpha"), "three": _payload("three", "other"),
        }, plan={"source_budgets": {"code": 1.0}, "target_repositories": ["alpha"],
                 "analysis_diagnostics": {"deterministic_parse": {"provenance": {"target_repositories": [
                     {"source": "explicit_query_reference", "value": "alpha"}]}}}})
        first = shadow_select(frozen).as_dict()
        second = shadow_select(frozen).as_dict()
        self.assertEqual(first["stage_m_order"], ["one", "two", "three"])
        self.assertEqual(first["stage_p_order"], second["stage_p_order"])
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_source_type_copy_has_production_parity(self) -> None:
        root = Path(__file__).resolve().parents[2]
        source = (root / "src/panda_agent/retrieval.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        production_node = next(
            node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_source_type_of"
        )
        namespace: dict[str, Any] = {"Any": Any}
        exec(compile(ast.Module(body=[production_node], type_ignores=[]), "retrieval.py", "exec"), namespace)
        production_source_type = namespace["_source_type_of"]
        items = [
            _payload("paper", "li_2026"), _payload("docs", "repository", "docs/page.rst"),
            _payload("workflow", object_type="workflow"), _payload("readme", object_type="readme_section"),
            _payload("code"),
        ]
        self.assertEqual([_source_type_of(item) for item in items], [production_source_type(item) for item in items])

    def test_no_benchmark_specific_identifiers_in_contract_or_fixtures(self) -> None:
        root = Path(__file__).resolve().parents[2]
        text = (root / "src/panda_agent/evidence_selection.py").read_text(encoding="utf-8")
        self.assertNotIn("MINIMUM", " ".join(c.value for c in ConstraintType))
        self.assertNotIn("benchmark", text.casefold())
        self.assertEqual(POLICY_ID, "c7.explicit_selection.v1")

    def test_production_wiring_is_structurally_isolated(self) -> None:
        root = Path(__file__).resolve().parents[2]
        retrieval = (root / "src/panda_agent/retrieval.py").read_text(encoding="utf-8")
        tree = ast.parse(retrieval)
        retrieve = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "retrieve")
        calls = [node.func.id for node in ast.walk(retrieve) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
        self.assertIn("select_final_evidence", calls)
        self.assertNotIn("evidence_selection", retrieval)
        self.assertIn("RERANK_SYSTEM_PROMPT", retrieval)
        self.assertIn('weights = {"exact": 2.0', retrieval)


if __name__ == "__main__":
    unittest.main()
