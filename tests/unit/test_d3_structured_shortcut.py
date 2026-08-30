from inspect import signature
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from panda_agent.config import load_query_expansions
from panda_agent.d3_structured import (
    SELECTED_D3_RULE_IDS,
    D3Arm,
    D3ExperimentConfig,
    D3StructuredContribution,
    build_structured_contribution,
    select_matching_query_expansions,
)
from panda_agent.entity_resolution import (
    AMBIGUOUS,
    RESOLVED_MULTIPLE,
    RESOLVED_UNIQUE,
    UNRESOLVED,
    D2Evidence,
    D2Resolution,
    D2ResolutionReceipt,
)
from panda_agent.models import RetrievalPlan
from panda_agent.retrieval import Retriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _rule(rule_id, trigger, *, symbol="", concept=""):
    return SimpleNamespace(
        rule_id=rule_id,
        triggers=[trigger],
        symbols=[symbol] if symbol else [],
        concepts=[concept] if concept else [],
        repositories=[],
        paper_page_hints={},
    )


class _ExplodingSelectedRule:
    rule_id = SELECTED_D3_RULE_IDS[0]
    triggers = ["synthetic selected marker"]

    def __getattr__(self, name):
        if name in {"symbols", "concepts", "repositories", "paper_page_hints"}:
            raise AssertionError("suppressed selected payload was accessed")
        raise AttributeError(name)


class _FailingStorage:
    def connect(self):
        raise RuntimeError("no database in deterministic preparse test")


class _Resolver:
    def __init__(self, receipt):
        self.receipt = receipt
        self.calls = []

    def resolve_shadow(self, question, plan):
        self.calls.append((question, plan))
        return self.receipt


class _GraphReader:
    def __init__(self, rows, relations, workflows):
        self.rows = {row["object_id"]: row for row in rows}
        self.relations = relations
        self.workflows = workflows

    def load_objects(self, object_ids):
        return [self.rows[value] for value in object_ids if value in self.rows]

    def load_accepted_relations(self, object_ids):
        active = set(object_ids)
        return [
            edge
            for edge in self.relations
            if edge["subject_id"] in active or edge["object_id"] in active
        ]

    def load_curated_workflow_steps(self, object_ids):
        active = set(object_ids)
        return [
            step
            for step in self.workflows
            if active.intersection(
                {
                    step["workflow_id"],
                    step["step_id"],
                    *(step["payload"].get("inputs", [])),
                    *(step["payload"].get("outputs", [])),
                    *(step["payload"].get("predecessor_step_ids", [])),
                    *(step["payload"].get("successor_step_ids", [])),
                }
            )
        ]


def _object(object_id):
    return {
        "object_id": object_id,
        "source_id": "pandaroot",
        "source_version_id": "pandaroot@locked",
        "object_type": "concept",
        "title": object_id,
        "text": f"Synthetic object {object_id}",
        "authority_level": "SOURCE",
        "locator": {"path": f"synthetic/{object_id}"},
        "metadata": {},
        "canonical_locator": object_id,
    }


def _evidence(tier, kind, object_id):
    return D2Evidence(
        tier=tier,
        kind=kind,
        matched_value=object_id,
        object_id=object_id,
        detail="synthetic unit-test evidence",
    )


class D3ArmTests(unittest.TestCase):
    def test_arm_contract_rejects_hybrid_or_different_rule_set(self):
        for arm in D3Arm:
            config = D3ExperimentConfig.for_arm(arm)
            self.assertEqual(config.structured_treatment_enabled, arm is D3Arm.STRUCTURED)
            self.assertEqual(config.selected_rule_ids, SELECTED_D3_RULE_IDS)
        with self.assertRaises(ValueError):
            D3ExperimentConfig(
                arm=D3Arm.ABLATION,
                structured_treatment_enabled=True,
            )
        with self.assertRaises(ValueError):
            D3ExperimentConfig(
                arm=D3Arm.STRUCTURED,
                selected_rule_ids=SELECTED_D3_RULE_IDS[:-1],
                structured_treatment_enabled=True,
            )

    def test_suppression_happens_before_selected_payload_access(self):
        decision = select_matching_query_expansions(
            "A synthetic selected marker for plumbing only.",
            [_ExplodingSelectedRule()],
            D3ExperimentConfig.for_arm(D3Arm.ABLATION),
        )
        self.assertEqual(decision.active_matching_rules, ())
        self.assertEqual(decision.suppressed_selected_rule_ids, (SELECTED_D3_RULE_IDS[0],))

    def test_real_54_rule_inventory_has_exact_three_arm_semantics(self):
        rules = load_query_expansions(
            PROJECT_ROOT / "configs" / "query_expansions.yaml"
        ).rules
        self.assertEqual(len(rules), 54)
        question = " || ".join(rule.triggers[0] for rule in rules)
        rule_ids = {rule.rule_id for rule in rules}
        self.assertTrue(set(SELECTED_D3_RULE_IDS).issubset(rule_ids))

        default = select_matching_query_expansions(question, rules, None)
        legacy = select_matching_query_expansions(
            question, rules, D3ExperimentConfig.for_arm(D3Arm.LEGACY)
        )
        self.assertEqual(
            {rule.rule_id for rule in default.active_matching_rules}, rule_ids
        )
        self.assertEqual(
            {rule.rule_id for rule in legacy.active_matching_rules}, rule_ids
        )
        for arm in (D3Arm.ABLATION, D3Arm.STRUCTURED):
            decision = select_matching_query_expansions(
                question, rules, D3ExperimentConfig.for_arm(arm)
            )
            self.assertEqual(
                {rule.rule_id for rule in decision.active_matching_rules},
                rule_ids - set(SELECTED_D3_RULE_IDS),
            )
            self.assertEqual(
                set(decision.suppressed_selected_rule_ids),
                set(SELECTED_D3_RULE_IDS),
            )

    def test_default_and_explicit_legacy_preserve_payload_semantics(self):
        selected = _rule(
            SELECTED_D3_RULE_IDS[0],
            "synthetic selected marker",
            symbol="SelectedSymbol",
        )
        retained = _rule(
            "unselected_synthetic_rule",
            "synthetic retained marker",
            concept="retained concept",
        )
        retriever = Retriever.__new__(Retriever)
        retriever.storage = _FailingStorage()
        retriever.fixed_versions = {"pandaroot": "locked"}
        retriever.policies = SimpleNamespace(intent_routes={})
        retriever.query_expansions = SimpleNamespace(rules=[selected, retained])
        question = "Synthetic selected marker plus synthetic retained marker."

        default = retriever._preparse(question)
        legacy = retriever._preparse(
            question,
            d3_config=D3ExperimentConfig.for_arm(D3Arm.LEGACY),
        )
        for field_name in (
            "matched_expansion_rules",
            "symbols",
            "concepts",
            "target_repositories",
            "paper_page_hints",
            "provenance",
        ):
            self.assertEqual(getattr(default, field_name), getattr(legacy, field_name))
        self.assertIsNone(default.d3_experiment)
        self.assertEqual(legacy.d3_experiment["d3_arm"], "LEGACY")

        for arm in (D3Arm.ABLATION, D3Arm.STRUCTURED):
            parsed = retriever._preparse(
                question,
                d3_config=D3ExperimentConfig.for_arm(arm),
            )
            self.assertNotIn(SELECTED_D3_RULE_IDS[0], parsed.matched_expansion_rules)
            self.assertNotIn("SelectedSymbol", parsed.symbols)
            self.assertIn("unselected_synthetic_rule", parsed.matched_expansion_rules)
            self.assertIn("retained concept", parsed.concepts)
            self.assertEqual(
                parsed.d3_experiment["suppressed_selected_rule_ids"],
                [SELECTED_D3_RULE_IDS[0]],
            )

    def test_experimental_plan_requires_matching_runtime_config(self):
        config = D3ExperimentConfig.for_arm(D3Arm.ABLATION)
        plan = SimpleNamespace(
            analysis_diagnostics={
                "d3_experiment": {
                    "d3_arm": "ABLATION",
                    "selected_rule_ids": list(SELECTED_D3_RULE_IDS),
                    "structured_treatment_enabled": False,
                    "selected_legacy_rules_suppressed": True,
                }
            }
        )
        self.assertEqual(Retriever._validate_d3_plan(plan, config)["d3_arm"], "ABLATION")
        with self.assertRaises(ValueError):
            Retriever._validate_d3_plan(
                plan,
                D3ExperimentConfig.for_arm(D3Arm.STRUCTURED),
            )

    @staticmethod
    def _empty_retriever():
        retriever = Retriever.__new__(Retriever)
        retriever.policies = SimpleNamespace(
            candidate_pool_per_channel=5,
            max_relation_hops=2,
            final_evidence_limit=3,
        )
        retriever.context_sources = []
        retriever.storage = object()
        retriever.vertex = SimpleNamespace(
            generate_json=lambda *args, **kwargs: {"ranked_object_ids": []}
        )
        retriever._exact = lambda *args: []
        retriever._vector = lambda question, *args: (
            [],
            [],
            [],
            SimpleNamespace(
                text=question,
                raw_question=question,
                components=[],
                excluded_component_classes=[],
                as_dict=lambda: {},
            ),
        )
        retriever._paper = lambda *args: []
        retriever._workflow = lambda *args: []
        retriever._graph = lambda *args: []
        return retriever

    @staticmethod
    def _plan(config=None):
        diagnostics = {}
        if config is not None:
            diagnostics["d3_experiment"] = {
                **select_matching_query_expansions(
                    "Synthetic query", [], config
                ).diagnostics(config)
            }
        return RetrievalPlan(
            intent="api",
            target_repositories=[],
            resolved_versions={},
            concepts=[],
            symbols=[],
            concept_scopes={},
            source_budgets={"code": 1.0},
            required_source_types=[],
            analysis_diagnostics=diagnostics,
        )

    def test_retrieve_default_shape_and_arm_activation_are_explicit(self):
        retriever = self._empty_retriever()
        default = retriever.retrieve("Synthetic query", self._plan())
        self.assertNotIn("d3_experiment", default)

        for arm in (D3Arm.LEGACY, D3Arm.ABLATION):
            config = D3ExperimentConfig.for_arm(arm)
            with patch(
                "panda_agent.retrieval.build_structured_contribution_from_storage"
            ) as structured:
                result = retriever.retrieve(
                    "Synthetic query", self._plan(config), d3_config=config
                )
            structured.assert_not_called()
            self.assertEqual(result["d3_experiment"]["d3_arm"], arm.value)
            self.assertEqual(
                result["d3_experiment"]["diagnostic_counters"][
                    "structured_resolution_attempt_count"
                ],
                0,
            )

        config = D3ExperimentConfig.for_arm(D3Arm.STRUCTURED)
        contribution = D3StructuredContribution(
            diagnostic_counters={
                "structured_resolution_attempt_count": 1,
                "structured_resolution_status_counts": {},
                "structured_resolution_hit_count": 0,
                "structured_seed_count": 0,
                "structured_relation_traversal_count": 0,
                "structured_workflow_traversal_count": 0,
                "structured_candidate_injection_count": 0,
                "migration_specific_direct_answer_location_injection_count": 0,
                "prohibited_fallback_use_count": 0,
                "evaluation_metadata_runtime_use_count": 0,
                "selected_legacy_payload_reuse_count": 0,
                "same_as_activation_count": 0,
            }
        )
        with patch(
            "panda_agent.retrieval.build_structured_contribution_from_storage",
            return_value=contribution,
        ) as structured:
            result = retriever.retrieve(
                "Synthetic query", self._plan(config), d3_config=config
            )
        structured.assert_called_once()
        self.assertTrue(result["d3_experiment"]["structured_treatment_enabled"])
        self.assertEqual(
            result["d3_experiment"]["diagnostic_counters"][
                "structured_resolution_attempt_count"
            ],
            1,
        )


class D3StructuredTraversalTests(unittest.TestCase):
    def test_generic_d2_to_d1_traversal_is_bounded_and_provenance_rich(self):
        question = "How do Alpha, Beta, Gamma, and Delta connect?"
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution(
                    "Alpha", "governed_id", "Alpha", RESOLVED_UNIQUE,
                    matched_object_id="g", canonical_object_id="canonical-g",
                    evidence=[_evidence("G", "governed_id", "g")],
                ),
                D2Resolution(
                    "Beta", "explicit_identifier", "Beta", RESOLVED_UNIQUE,
                    matched_object_id="s", canonical_object_id="identity-target",
                    evidence=[
                        _evidence("S", "exact_symbol", "s"),
                        _evidence("G", "same_as", "identity-target"),
                    ],
                ),
                D2Resolution(
                    "Gamma", "descriptive", "Gamma", RESOLVED_UNIQUE,
                    matched_object_id="d", canonical_object_id="must-not-promote",
                    evidence=[_evidence("D", "descriptive_bundle", "d")],
                ),
                D2Resolution(
                    "Delta", "descriptive", "Delta", AMBIGUOUS,
                    candidates=[
                        {"object_id": "d-amb-2", "tier": "D"},
                        {"object_id": "d-amb-1", "tier": "D"},
                    ],
                ),
                D2Resolution(
                    "Correction", "accepted_alias", "Correction", UNRESOLVED,
                    candidates=[{"object_id": "corrective", "tier": "G"}],
                    diagnostics={"corrective": True},
                ),
                D2Resolution(
                    question, "descriptive", question, UNRESOLVED,
                ),
                D2Resolution(
                    "Many", "governed_id", "Many", RESOLVED_MULTIPLE,
                    selected_object_ids=["multi-1", "multi-2"],
                ),
                D2Resolution("Unknown", "descriptive", "Unknown", UNRESOLVED),
            ]
        )
        rows = [
            _object(value)
            for value in (
                "g", "s", "d", "d-amb-1", "d-amb-2", "corrective",
                "r1", "r2", "r3", "same-as-target", "rejected-target",
                "pending-target", "w1", "w2",
            )
        ]
        relations = [
            {
                "edge_id": "e1", "subject_id": "s", "predicate": "USES",
                "object_id": "r1", "review_status": "accepted",
            },
            {
                "edge_id": "e2", "subject_id": "r1", "predicate": "PRODUCES",
                "object_id": "r2", "review_status": "accepted",
            },
            {
                "edge_id": "e3", "subject_id": "r2", "predicate": "CALLS",
                "object_id": "r3", "review_status": "accepted",
            },
            {
                "edge_id": "cycle", "subject_id": "r1", "predicate": "RELATED_TO",
                "object_id": "s", "review_status": "accepted",
            },
            {
                "edge_id": "same", "subject_id": "g", "predicate": "SAME_AS",
                "object_id": "same-as-target", "review_status": "accepted",
            },
            {
                "edge_id": "rejected", "subject_id": "g", "predicate": "USES",
                "object_id": "rejected-target", "review_status": "rejected",
            },
            {
                "edge_id": "pending", "subject_id": "g", "predicate": "USES",
                "object_id": "pending-target", "review_status": "pending",
            },
        ]
        workflows = [
            {
                "workflow_id": "wf",
                "step_id": "step-1",
                "name": "Synthetic first step",
                "payload": {"inputs": ["d"], "outputs": ["w1"]},
            },
            {
                "workflow_id": "wf",
                "step_id": "step-2",
                "name": "Synthetic second step",
                "payload": {"inputs": ["w1"], "outputs": ["w2"]},
            },
        ]
        result = build_structured_contribution(
            question,
            {
                "target_repositories": ["pandaroot"],
                "resolved_versions": {"pandaroot": "locked"},
                "analysis_diagnostics": {"analyzer_accepted_semantic_delta": {"concepts": []}},
            },
            resolver=_Resolver(receipt),
            graph_reader=_GraphReader(rows, relations, workflows),
            max_relation_hops=2,
        )

        object_ids = [row["object_id"] for row in result.candidates]
        for expected in ("g", "s", "d", "d-amb-1", "d-amb-2", "corrective", "r1", "r2", "w1", "w2"):
            self.assertIn(expected, object_ids)
        for prohibited in (
            "r3", "same-as-target", "rejected-target", "pending-target",
            "multi-1", "multi-2",
        ):
            self.assertNotIn(prohibited, object_ids)

        provenance = {
            row["candidate_object_id"]: row for row in result.candidate_provenance
        }
        self.assertEqual(provenance["g"]["canonical_object_id"], "canonical-g")
        self.assertIsNone(provenance["s"]["canonical_object_id"])
        self.assertEqual(provenance["s"]["evidence_tier"], "S")
        self.assertIsNone(provenance["r1"]["canonical_object_id"])
        self.assertEqual(provenance["d"]["authority_class"], "NONAUTHORITATIVE_ADVISORY")
        self.assertEqual(
            provenance["corrective"]["candidate_identity_authority"],
            "NONAUTHORITATIVE_ADVISORY",
        )
        self.assertEqual(
            [edge["predicate"] for edge in provenance["r2"]["relation_path"]],
            ["USES", "PRODUCES"],
        )
        self.assertEqual(provenance["w2"]["workflow_step"]["step_id"], "step-2")
        self.assertIn(
            "whole_question_fallback_prohibited",
            {row["reason"] for row in result.excluded_resolution_reasons},
        )
        counters = result.diagnostic_counters
        self.assertEqual(counters["structured_resolution_attempt_count"], 1)
        self.assertEqual(counters["structured_candidate_injection_count"], len(object_ids))
        self.assertEqual(counters["migration_specific_direct_answer_location_injection_count"], 0)
        self.assertEqual(counters["prohibited_fallback_use_count"], 0)
        self.assertEqual(counters["selected_legacy_payload_reuse_count"], 0)
        self.assertEqual(counters["same_as_activation_count"], 0)

    def test_runtime_api_rejects_out_of_bound_hops_and_evaluation_metadata(self):
        resolver = _Resolver(D2ResolutionReceipt())
        reader = _GraphReader([], [], [])
        with self.assertRaises(ValueError):
            build_structured_contribution(
                "Synthetic question",
                {"target_repositories": [], "resolved_versions": {}},
                resolver=resolver,
                graph_reader=reader,
                max_relation_hops=3,
            )
        with self.assertRaises(TypeError):
            build_structured_contribution(
                "Synthetic question",
                {"target_repositories": [], "resolved_versions": {}},
                resolver=resolver,
                graph_reader=reader,
                case_id="forbidden",
            )
        forbidden = {
            "case_id", "question_id", "expected_status", "comparison_role",
            "expected_evidence_ids", "bound_rule_id",
        }
        self.assertTrue(
            forbidden.isdisjoint(signature(build_structured_contribution).parameters)
        )
        self.assertTrue(forbidden.isdisjoint(signature(Retriever.retrieve).parameters))


if __name__ == "__main__":
    unittest.main()
