"""Unit and synthetic tests for D3.5-A1 Bounded Structured Evidence-Link Bridging Prototype."""

from inspect import signature
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from panda_agent.d3_structured import (
    GLOBAL_BRIDGED_CANDIDATE_CAP,
    GLOBAL_REACHABLE_STRUCTURE_CAP,
    SELECTED_D3_RULE_IDS,
    D3_5_SELECTED_RULE_IDS,
    SHARED_SEED_CAP,
    D3Arm,
    D3_5Arm,
    D3ExperimentConfig,
    D3_5ExperimentConfig,
    D3StructuredContribution,
    PostgresD3StructuredGraphReader,
    derive_unbridged_structured_seeds,
    derive_d3_5_bridge_seeds,
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


class _MockResolver:
    def __init__(self, receipt: D2ResolutionReceipt):
        self.receipt = receipt
        self.calls = []

    def resolve_shadow(self, question, plan):
        self.calls.append((question, plan))
        return self.receipt


class _MockGraphReader:
    def __init__(self, rows=(), relations=(), workflows=(), workflow_steps=(), source_files=()):
        self.rows = {row["object_id"]: row for row in rows}
        self.relations = list(relations)
        self.workflows = list(workflows) + list(workflow_steps)
        self.source_files = list(source_files)

    def load_objects(self, object_ids):
        return [self.rows[oid] for oid in object_ids if oid in self.rows]

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
                    step.get("workflow_id"),
                    step.get("step_id"),
                    *(step.get("payload", {}).get("inputs", [])),
                    *(step.get("payload", {}).get("outputs", [])),
                    *(step.get("payload", {}).get("predecessor_step_ids", [])),
                    *(step.get("payload", {}).get("successor_step_ids", [])),
                }
            )
        ]

    def find_source_objects_by_path(self, source_id, path):
        return [
            row for row in self.source_files
            if row.get("source_id") == source_id
            and (
                (row.get("locator") or {}).get("path") == path
                or row.get("canonical_locator") == path
            )
        ]


def _gov_object(object_id, *, parent_id=None, source_id="curated_panda_domain", source_version_id=None, obj_type=None):
    if obj_type is None:
        if object_id.startswith("workflow"):
            obj_type = "workflow"
        elif object_id.startswith("data_product") or object_id.startswith("root_tree"):
            obj_type = "data_product"
        elif object_id.startswith("repository"):
            obj_type = "repository_version"
        elif object_id.startswith("subsystem"):
            obj_type = "subsystem"
        elif object_id.startswith("paper") or object_id.startswith("document"):
            obj_type = "document_reference"
        elif object_id.startswith("configuration"):
            obj_type = "configuration_key"
        elif object_id.startswith("file_pattern"):
            obj_type = "file_pattern"
        elif object_id.startswith("concept"):
            obj_type = "physics_concept"
        else:
            obj_type = "concept"
    metadata = {}
    if parent_id:
        metadata["parent_object_id"] = parent_id
    if source_version_id is None:
        source_version_id = f"{source_id}@locked"
    return {
        "object_id": object_id,
        "source_id": source_id,
        "source_version_id": source_version_id,
        "object_type": obj_type,
        "title": object_id,
        "text": f"Governed entity {object_id}",
        "authority_level": "SOURCE",
        "locator": {"path": f"governed/{object_id}"},
        "metadata": metadata,
        "canonical_locator": object_id,
    }


def _source_file_obj(object_id, source_id, rel_path, *, obj_type="source_file"):
    return {
        "object_id": object_id,
        "source_id": source_id,
        "source_version_id": f"{source_id}@locked",
        "object_type": obj_type,
        "title": rel_path,
        "text": f"Source code of {rel_path}",
        "authority_level": "primary",
        "locator": {"path": rel_path, "start_line": 1, "end_line": 100},
        "metadata": {},
        "canonical_locator": rel_path,
    }


def _d2_evidence(tier, kind, object_id):
    return D2Evidence(
        tier=tier,
        kind=kind,
        matched_value=object_id,
        object_id=object_id,
        detail="synthetic D3.5 unit-test evidence",
    )


class D3_5_FourArmAndPlumbingTests(unittest.TestCase):
    def test_four_arms_initialization_and_properties(self):
        # Historical D3 (7 rules)
        hist_legacy = D3ExperimentConfig.for_arm(D3Arm.LEGACY)
        self.assertEqual(hist_legacy.selected_rule_ids, SELECTED_D3_RULE_IDS)
        self.assertFalse(hist_legacy.structured_treatment_enabled)
        self.assertFalse(hist_legacy.bridge_enabled)

        hist_struct = D3ExperimentConfig.for_arm(D3Arm.STRUCTURED)
        self.assertEqual(hist_struct.selected_rule_ids, SELECTED_D3_RULE_IDS)
        self.assertTrue(hist_struct.structured_treatment_enabled)
        self.assertFalse(hist_struct.bridge_enabled)

        # D3.5 (2 focused rules)
        legacy = D3_5ExperimentConfig.for_arm(D3_5Arm.LEGACY)
        self.assertEqual(legacy.selected_rule_ids, D3_5_SELECTED_RULE_IDS)
        self.assertFalse(legacy.structured_treatment_enabled)
        self.assertFalse(legacy.bridge_enabled)
        self.assertFalse(legacy.selected_legacy_rules_suppressed)

        ablation = D3_5ExperimentConfig.for_arm(D3_5Arm.ABLATION)
        self.assertEqual(ablation.selected_rule_ids, D3_5_SELECTED_RULE_IDS)
        self.assertFalse(ablation.structured_treatment_enabled)
        self.assertFalse(ablation.bridge_enabled)
        self.assertTrue(ablation.selected_legacy_rules_suppressed)

        unbridged = D3_5ExperimentConfig.for_arm(D3_5Arm.STRUCTURED_UNBRIDGED)
        self.assertEqual(unbridged.selected_rule_ids, D3_5_SELECTED_RULE_IDS)
        self.assertTrue(unbridged.structured_treatment_enabled)
        self.assertFalse(unbridged.bridge_enabled)
        self.assertTrue(unbridged.selected_legacy_rules_suppressed)

        bridged = D3_5ExperimentConfig.for_arm(D3_5Arm.STRUCTURED_BRIDGED)
        self.assertEqual(bridged.selected_rule_ids, D3_5_SELECTED_RULE_IDS)
        self.assertTrue(bridged.structured_treatment_enabled)
        self.assertTrue(bridged.bridge_enabled)
        self.assertTrue(bridged.selected_legacy_rules_suppressed)

    def test_invalid_arm_configurations_fail_fast(self):
        with self.assertRaises(ValueError):
            D3_5ExperimentConfig(arm=D3_5Arm.STRUCTURED_UNBRIDGED, bridge_enabled=True, structured_treatment_enabled=True)
        with self.assertRaises(ValueError):
            D3_5ExperimentConfig(arm=D3_5Arm.STRUCTURED_BRIDGED, bridge_enabled=False, structured_treatment_enabled=True)
        with self.assertRaises(ValueError):
            D3_5ExperimentConfig(arm=D3_5Arm.ABLATION, structured_treatment_enabled=True)
        with self.assertRaises(ValueError):
            D3_5ExperimentConfig(arm=D3_5Arm.LEGACY, selected_rule_ids=("unknown_rule",))
        with self.assertRaises(ValueError):
            D3ExperimentConfig(arm=D3Arm.STRUCTURED, selected_rule_ids=D3_5_SELECTED_RULE_IDS)


class D3_5_SeedAuthorityAndAmbiguityTests(unittest.TestCase):
    def test_tier_g_s_d_unique_and_excluded_seeds(self):
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("G_seed", "governed_id", "G_seed", RESOLVED_UNIQUE,
                             matched_object_id="g_obj", canonical_object_id="canon_g",
                             evidence=[_d2_evidence("G", "governed_id", "g_obj")]),
                D2Resolution("S_seed", "explicit_identifier", "S_seed", RESOLVED_UNIQUE,
                             matched_object_id="s_obj", canonical_object_id="ignore_same_as",
                             evidence=[_d2_evidence("S", "exact_symbol", "s_obj"), _d2_evidence("G", "same_as", "ignore_same_as")]),
                D2Resolution("D_seed", "descriptive", "D_seed", RESOLVED_UNIQUE,
                             matched_object_id="d_obj", canonical_object_id="ignore_d",
                             evidence=[_d2_evidence("D", "descriptive_bundle", "d_obj")]),
                D2Resolution("Unresolved_seed", "descriptive", "Unresolved_seed", UNRESOLVED),
                D2Resolution("Multi_seed", "governed_id", "Multi_seed", RESOLVED_MULTIPLE,
                             selected_object_ids=["m1", "m2"]),
                D2Resolution("Corrective_seed", "accepted_alias", "Corrective_seed", UNRESOLVED,
                             candidates=[{"object_id": "corr_obj", "tier": "G"}],
                             diagnostics={"corrective": True}),
            ]
        )
        rows = [_gov_object(oid) for oid in ("g_obj", "s_obj", "d_obj", "corr_obj", "m1", "m2")]
        reader = _MockGraphReader(rows=rows)
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Test query", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )

        cand_ids = [c["object_id"] for c in result.candidates]
        # Tier G, S, D admitted
        self.assertIn("g_obj", cand_ids)
        self.assertIn("s_obj", cand_ids)
        self.assertIn("d_obj", cand_ids)
        # Corrective seed admitted without traversal
        self.assertIn("corr_obj", cand_ids)
        # Unresolved and Multi not admitted
        self.assertNotIn("m1", cand_ids)
        self.assertNotIn("m2", cand_ids)

        # Check provenance metadata on admitted seeds
        prov_map = {p["candidate_object_id"]: p for p in result.candidate_provenance}
        self.assertEqual(prov_map["g_obj"]["authority_class"], "AUTHORITATIVE_BOUNDED_IDENTITY")
        self.assertEqual(prov_map["s_obj"]["authority_class"], "AUTHORITATIVE_BOUNDED_MATCHED_RECORD")
        self.assertEqual(prov_map["d_obj"]["authority_class"], "NONAUTHORITATIVE_ADVISORY")
        self.assertEqual(prov_map["corr_obj"]["authority_class"], "NONAUTHORITATIVE_ADVISORY")

    def test_atomic_tier_d_ambiguity_set_rules(self):
        # Case 1: Ambiguity set of 3 <= 8 and fits remaining budget -> all 3 admitted
        receipt_fit = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("G_seed", "governed_id", "G_seed", RESOLVED_UNIQUE,
                             matched_object_id="g1", canonical_object_id="canon_g1",
                             evidence=[_d2_evidence("G", "governed_id", "g1")]),
                D2Resolution("Amb_set", "descriptive", "Amb_set", AMBIGUOUS,
                             candidates=[
                                 {"object_id": "amb1", "tier": "D"},
                                 {"object_id": "amb2", "tier": "D"},
                                 {"object_id": "amb3", "tier": "D"},
                             ]),
            ]
        )
        rows = [_gov_object(oid) for oid in ("g1", "amb1", "amb2", "amb3")]
        reader = _MockGraphReader(rows=rows)
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result_fit = build_structured_contribution(
            "Test fit", plan, resolver=_MockResolver(receipt_fit), graph_reader=reader, bridge_enabled=True
        )
        cand_ids_fit = [c["object_id"] for c in result_fit.candidates]
        self.assertIn("g1", cand_ids_fit)
        self.assertIn("amb1", cand_ids_fit)
        self.assertIn("amb2", cand_ids_fit)
        self.assertIn("amb3", cand_ids_fit)

        # Case 2: Ambiguity set of 9 (> 8):
        # Unbridged baseline admits all 9 (frozen historical behavior).
        # Bridge branch rejects ambiguity set atomically and emits AMBIGUITY_SET_EXCEEDS_SAFE_SEED_BUDGET.
        receipt_oversize = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("Amb_large", "descriptive", "Amb_large", AMBIGUOUS,
                             candidates=[{"object_id": f"large_{i}", "tier": "D"} for i in range(9)]),
            ]
        )
        large_rows = [_gov_object(f"large_{i}") for i in range(9)]
        reader_large = _MockGraphReader(rows=large_rows)
        result_large = build_structured_contribution(
            "Test oversize", plan, resolver=_MockResolver(receipt_oversize), graph_reader=reader_large, bridge_enabled=True
        )
        self.assertEqual(len(result_large.candidates), 9)
        self.assertEqual(len(result_large.reachability_receipts), 1)
        self.assertEqual(result_large.reachability_receipts[0]["reachability_status"], "NO_ELIGIBLE_STRUCTURED_SEED")
        reasons = [e["reason"] for e in result_large.excluded_resolution_reasons]
        self.assertIn("AMBIGUITY_SET_EXCEEDS_SAFE_SEED_BUDGET", reasons)

        # Case 3: 7 G-seeds consume budget, ambiguity set of 2 (> remaining 1):
        # Unbridged baseline admits all 9.
        # Bridge branch admits 7 G-seeds, rejects ambiguity set atomically.
        g_resolutions = [
            D2Resolution(f"G_{i}", "governed_id", f"G_{i}", RESOLVED_UNIQUE,
                         matched_object_id=f"g_{i}", canonical_object_id=f"canon_g_{i}",
                         evidence=[_d2_evidence("G", "governed_id", f"g_{i}")])
            for i in range(7)
        ]
        g_resolutions.append(
            D2Resolution("Amb_exceed", "descriptive", "Amb_exceed", AMBIGUOUS,
                         candidates=[{"object_id": "overflow1", "tier": "D"}, {"object_id": "overflow2", "tier": "D"}])
        )
        receipt_exceed = D2ResolutionReceipt(resolutions=g_resolutions)
        exceed_rows = [_gov_object(f"g_{i}") for i in range(7)] + [_gov_object("overflow1"), _gov_object("overflow2")]
        reader_exceed = _MockGraphReader(rows=exceed_rows)
        result_exceed = build_structured_contribution(
            "Test exceed budget", plan, resolver=_MockResolver(receipt_exceed), graph_reader=reader_exceed, bridge_enabled=True
        )
        cand_ids_exceed = [c["object_id"] for c in result_exceed.candidates]
        self.assertEqual(len(cand_ids_exceed), 9)
        exceed_reasons = [e["reason"] for e in result_exceed.excluded_resolution_reasons]
        self.assertIn("AMBIGUITY_SET_EXCEEDS_SAFE_SEED_BUDGET", exceed_reasons)
        bridge_seed_ids = {r["seed_object_id"] for r in result_exceed.reachability_receipts if r["seed_object_id"]}
        self.assertEqual(len(bridge_seed_ids), 7)
        self.assertNotIn("overflow1", bridge_seed_ids)
        self.assertNotIn("overflow2", bridge_seed_ids)


class D3_5_MechanismAReachabilityTests(unittest.TestCase):
    def test_upward_containment_and_semantic_reachability(self):
        # Tree node with parent_object_id
        child_node = _gov_object("data_product.restgas.event_poca", parent_id="data_product.restgas.boost_root")
        parent_node = _gov_object("data_product.restgas.boost_root")
        workflow_node = _gov_object("workflow.restgas.first_pass_poca")
        rows = [child_node, parent_node, workflow_node]

        # Accepted PRODUCES edge from workflow to parent
        relations = [
            {
                "edge_id": "edge_produces",
                "subject_id": "workflow.restgas.first_pass_poca",
                "predicate": "PRODUCES",
                "object_id": "data_product.restgas.boost_root",
                "review_status": "accepted",
                "payload": {
                    "evidence_paths": ["macro/target/ana_dpm.C"],
                    "evidence_source_ids": ["restgas_determination"],
                },
            },
            {
                "edge_id": "edge_denied_predicate",
                "subject_id": "data_product.restgas.boost_root",
                "predicate": "NON_ALLOWLISTED_PREDICATE",
                "object_id": "some_random_node",
                "review_status": "accepted",
                "payload": {},
            },
            {
                "edge_id": "edge_same_as_denied",
                "subject_id": "data_product.restgas.boost_root",
                "predicate": "SAME_AS",
                "object_id": "same_as_target",
                "review_status": "accepted",
                "payload": {},
            },
        ]
        source_file = _source_file_obj("obj_ana_dpm", "restgas_determination", "macro/target/ana_dpm.C")
        reader = _MockGraphReader(rows=rows, relations=relations, source_files=[source_file])

        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("event_poca", "explicit_identifier", "event_poca", RESOLVED_UNIQUE,
                             matched_object_id="data_product.restgas.event_poca", canonical_object_id=None,
                             evidence=[_d2_evidence("S", "exact_symbol", "data_product.restgas.event_poca")]),
            ]
        )
        plan = {
            "target_repositories": ["restgas_determination", "pandaroot"],
            "resolved_versions": {"restgas_determination": "locked", "pandaroot": "locked"},
        }
        result = build_structured_contribution(
            "What produces event_poca?", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )

        # Baseline seed
        cand_ids = [c["object_id"] for c in result.candidates]
        self.assertIn("data_product.restgas.event_poca", cand_ids)

        # Verify reachability receipts
        self.assertTrue(len(result.reachability_receipts) > 0)
        reached_nodes = {nid for r in result.reachability_receipts for nid in r["structural_path"]["node_ids"]}
        # Child reached (Seed)
        self.assertIn("data_product.restgas.event_poca", reached_nodes)
        # Parent reached (Upward Containment)
        self.assertIn("data_product.restgas.boost_root", reached_nodes)
        # Neighbor reached (Semantic Reachability via PRODUCES reverse)
        self.assertIn("workflow.restgas.first_pass_poca", reached_nodes)
        # Denied predicate not reached
        self.assertNotIn("some_random_node", reached_nodes)
        self.assertNotIn("same_as_target", reached_nodes)

        reach_transition_types = [
            r["structural_path"]["transition_types"] for r in result.reachability_receipts
        ]
        self.assertTrue(any("CONTAINMENT_PARENT" in types for types in reach_transition_types))
        self.assertTrue(any("ACCEPTED_RELATION" in types for types in reach_transition_types))

        # Verify Mechanism B bridged source-native candidate
        bridged_ids = [c["object_id"] for c in result.bridged_candidates]
        self.assertIn("obj_ana_dpm", bridged_ids)
        self.assertEqual(result.diagnostic_counters["bridged_candidate_injection_count"], 1)

    def test_forked_from_is_forward_only_and_requires_both_repos_in_scope(self):
        repo_restgas = _gov_object("repository.restgas_determination.oct19", source_id="restgas_determination")
        repo_pandaroot = _gov_object("repository.pandaroot.oct19", source_id="pandaroot")
        relations = [
            {
                "edge_id": "edge_forked",
                "subject_id": "repository.restgas_determination.oct19",
                "predicate": "FORKED_FROM",
                "object_id": "repository.pandaroot.oct19",
                "review_status": "accepted",
                "payload": {
                    "evidence_paths": ["README.md"],
                    "evidence_source_ids": ["restgas_determination"],
                    "source_version_ids": ["restgas_determination@locked", "pandaroot@locked"],
                },
            }
        ]
        readme_obj = _source_file_obj("obj_readme", "restgas_determination", "README.md")
        reader = _MockGraphReader(rows=[repo_restgas, repo_pandaroot], relations=relations, source_files=[readme_obj])

        # Test forward traversal from restgas when both repos in scope
        plan_both = {
            "target_repositories": ["restgas_determination", "pandaroot"],
            "resolved_versions": {"restgas_determination": "locked", "pandaroot": "locked"},
        }
        receipt_forward = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("restgas_repo", "governed_id", "restgas_repo", RESOLVED_UNIQUE,
                             matched_object_id="repository.restgas_determination.oct19", canonical_object_id="repository.restgas_determination.oct19",
                             evidence=[_d2_evidence("G", "governed_id", "repository.restgas_determination.oct19")]),
            ]
        )
        res_forward = build_structured_contribution(
            "Test forward FORKED_FROM", plan_both, resolver=_MockResolver(receipt_forward), graph_reader=reader, bridge_enabled=True
        )
        forward_reached = {nid for r in res_forward.reachability_receipts for nid in r["structural_path"]["node_ids"]}
        self.assertIn("repository.pandaroot.oct19", forward_reached)
        self.assertIn("obj_readme", [c["object_id"] for c in res_forward.bridged_candidates])

        # Test reverse traversal from pandaroot -> DENIED (FORKED_FROM reverse is False)
        receipt_reverse = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("pandaroot_repo", "governed_id", "pandaroot_repo", RESOLVED_UNIQUE,
                             matched_object_id="repository.pandaroot.oct19", canonical_object_id="repository.pandaroot.oct19",
                             evidence=[_d2_evidence("G", "governed_id", "repository.pandaroot.oct19")]),
            ]
        )
        res_reverse = build_structured_contribution(
            "Test reverse FORKED_FROM", plan_both, resolver=_MockResolver(receipt_reverse), graph_reader=reader, bridge_enabled=True
        )
        reverse_reached = {nid for r in res_reverse.reachability_receipts for nid in r["structural_path"]["node_ids"]}
        self.assertNotIn("repository.restgas_determination.oct19", reverse_reached)
        self.assertEqual(len(res_reverse.bridged_candidates), 0)


class D3_5_MechanismBMaterializationTests(unittest.TestCase):
    def test_strict_path_normalization_and_rejection(self):
        gov_node = _gov_object("gov1", obj_type="workflow")
        relations = [
            {
                "edge_id": "e_invalid",
                "subject_id": "gov1",
                "predicate": "PRODUCES",
                "object_id": "gov2",
                "review_status": "accepted",
                "payload": {
                    "evidence_paths": ["/absolute/path.C", "../traversal/path.C", "C:\\windows\\path.C"],
                    "evidence_source_ids": ["pandaroot"],
                },
            }
        ]
        gov2 = _gov_object("gov2", obj_type="data_product")
        reader = _MockGraphReader(rows=[gov_node, gov2], relations=relations)
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov1", "governed_id", "gov1", RESOLVED_UNIQUE,
                             matched_object_id="gov1", canonical_object_id="gov1",
                             evidence=[_d2_evidence("G", "governed_id", "gov1")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Test invalid paths", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        path_statuses = [b["bridge_status"] for b in result.bridge_receipts if b["evidence_field_used"] == "evidence_paths"]
        self.assertTrue(all(s == "GOVERNED_PROVENANCE_INVALID" for s in path_statuses))
        self.assertEqual(len(path_statuses), 3)
        self.assertEqual(len(result.bridged_candidates), 0)

    def test_exact_path_and_evidence_object_ids_materialization(self):
        gov1 = _gov_object("gov1", obj_type="subsystem")
        relations = [
            {
                "edge_id": "e_valid",
                "subject_id": "gov1",
                "predicate": "IMPLEMENTS",
                "object_id": "gov_model",
                "review_status": "accepted",
                "payload": {
                    "evidence_paths": ["model/PndLmdModelFactory.cxx"],
                    "evidence_object_ids": ["direct_obj_1"],
                    "evidence_source_ids": ["luminosityfit"],
                },
            }
        ]
        gov_model = _gov_object("gov_model", obj_type="physics_concept")
        source_model = _source_file_obj("cand_model_factory", "luminosityfit", "model/PndLmdModelFactory.cxx")
        direct_obj = _source_file_obj("direct_obj_1", "luminosityfit", "direct/file.cxx")

        reader = _MockGraphReader(
            rows=[gov1, gov_model, direct_obj],
            relations=relations,
            source_files=[source_model, direct_obj],
        )
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov1", "governed_id", "gov1", RESOLVED_UNIQUE,
                             matched_object_id="gov1", canonical_object_id="gov1",
                             evidence=[_d2_evidence("G", "governed_id", "gov1")]),
            ]
        )
        plan = {"target_repositories": ["luminosityfit"], "resolved_versions": {"luminosityfit": "locked"}}
        result = build_structured_contribution(
            "Test valid materialization", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        bridged_ids = [c["object_id"] for c in result.bridged_candidates]
        self.assertIn("cand_model_factory", bridged_ids)
        self.assertIn("direct_obj_1", bridged_ids)
        statuses = [b["bridge_status"] for b in result.bridge_receipts]
        self.assertIn("BRIDGED_CANDIDATE_INJECTED", statuses)

    def test_materialization_is_terminal_and_capped_at_20(self):
        gov1 = _gov_object("gov1", obj_type="workflow")
        # 25 evidence paths
        paths = [f"src/file_{i}.cxx" for i in range(25)]
        relations = [
            {
                "edge_id": "e_many",
                "subject_id": "gov1",
                "predicate": "PRODUCES",
                "object_id": "gov2",
                "review_status": "accepted",
                "payload": {"evidence_paths": paths, "evidence_source_ids": ["pandaroot"]},
            }
        ]
        gov2 = _gov_object("gov2", obj_type="data_product")
        source_files = [_source_file_obj(f"src_obj_{i}", "pandaroot", f"src/file_{i}.cxx") for i in range(25)]
        # Add relation on source object to verify it is NOT traversed (terminal)
        relations.append({
            "edge_id": "e_source_leak",
            "subject_id": "src_obj_0",
            "predicate": "PRODUCES",
            "object_id": "leaked_neighbor",
            "review_status": "accepted",
            "payload": {},
        })
        leaked_node = _gov_object("leaked_neighbor")

        reader = _MockGraphReader(rows=[gov1, gov2, leaked_node], relations=relations, source_files=source_files)
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov1", "governed_id", "gov1", RESOLVED_UNIQUE,
                             matched_object_id="gov1", canonical_object_id="gov1",
                             evidence=[_d2_evidence("G", "governed_id", "gov1")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Test terminal and cap", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        self.assertEqual(len(result.bridged_candidates), GLOBAL_BRIDGED_CANDIDATE_CAP)
        self.assertEqual(result.diagnostic_counters["bridged_candidate_ranked_out_count"], 5)
        # Ensure leaked neighbor was NOT traversed from source candidate
        cand_ids = [c["object_id"] for c in result.candidates]
        self.assertNotIn("leaked_neighbor", cand_ids)


class D3_5_IntegrationAndDiagnosticsTests(unittest.TestCase):
    def test_retrieval_integration_prefix_precedence_and_seven_diagnostics(self):
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

        # Graph channel produces 5 ordinary candidates
        ordinary_graph = [_source_file_obj(f"ord_graph_{i}", "pandaroot", f"ord/file_{i}.cxx") for i in range(5)]
        retriever._graph = lambda *args: list(ordinary_graph)

        config = D3_5ExperimentConfig.for_arm(D3_5Arm.STRUCTURED_BRIDGED)
        plan = RetrievalPlan(
            intent="api",
            target_repositories=["pandaroot"],
            resolved_versions={"pandaroot": "locked"},
            concepts=[],
            symbols=[],
            concept_scopes={},
            source_budgets={"code": 1.0},
            required_source_types=[],
            analysis_diagnostics={
                "d3_experiment": {
                    "d3_arm": "STRUCTURED_BRIDGED",
                    "selected_rule_ids": list(D3_5_SELECTED_RULE_IDS),
                    "structured_treatment_enabled": True,
                    "bridge_enabled": True,
                    "selected_legacy_rules_suppressed": True,
                    "diagnostic_counters": {},
                    "suppressed_selected_rule_ids": [],
                }
            },
        )

        bridged_candidates = [
            _source_file_obj("bridged_1", "pandaroot", "bridged/file_1.cxx"),
            _source_file_obj("bridged_2", "pandaroot", "bridged/file_2.cxx"),
        ]
        contribution = D3StructuredContribution(
            candidates=[],
            bridged_candidates=bridged_candidates,
            candidate_provenance=[],
            reachability_receipts=[],
            bridge_receipts=[],
            diagnostic_counters={
                "structured_resolution_attempt_count": 1,
                "bridged_candidate_injection_count": 2,
                "selected_legacy_payload_reuse_count": 0,
                "evaluation_metadata_runtime_use_count": 0,
            },
        )

        with patch(
            "panda_agent.retrieval.build_structured_contribution_from_storage",
            return_value=contribution,
        ):
            res = retriever.retrieve("Synthetic integration test", plan, d3_config=config)

        d3_exp = res["d3_experiment"]
        self.assertEqual(d3_exp["d3_arm"], "STRUCTURED_BRIDGED")
        self.assertTrue(d3_exp["bridge_enabled"])

        disp = d3_exp["displacement_diagnostics"]
        # Seven exact displacement diagnostics
        self.assertEqual(disp["bridged_candidate_count"], 2)
        self.assertEqual(disp["graph_candidates_before_bridge"], 5)
        self.assertEqual(disp["graph_candidates_after_bridge"], 5)
        self.assertEqual(disp["graph_candidates_displaced_by_prefix"], 2)
        self.assertEqual(disp["displaced_object_ids"], ["ord_graph_3", "ord_graph_4"])
        self.assertEqual(disp["bridged_candidate_ids"], ["bridged_1", "bridged_2"])
        self.assertEqual(disp["deduplicated_overlap_count"], 0)

    def test_structured_unbridged_does_not_mislabel_bridged_diagnostics(self):
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
        retriever._dense = lambda *args: []
        retriever._sparse = lambda *args: []
        retriever._paper = lambda *args: []
        retriever._workflow = lambda *args: []
        ordinary_graph = [_source_file_obj(f"ord_graph_{i}", "pandaroot", f"ord/file_{i}.cxx") for i in range(5)]
        retriever._graph = lambda *args: list(ordinary_graph)

        config = D3_5ExperimentConfig.for_arm(D3_5Arm.STRUCTURED_UNBRIDGED)
        plan = RetrievalPlan(
            intent="api",
            target_repositories=["pandaroot"],
            resolved_versions={"pandaroot": "locked"},
            concepts=[],
            symbols=[],
            concept_scopes={},
            source_budgets={"code": 1.0},
            required_source_types=[],
            analysis_diagnostics={
                "d3_experiment": {
                    "d3_arm": "STRUCTURED_UNBRIDGED",
                    "selected_rule_ids": list(D3_5_SELECTED_RULE_IDS),
                    "structured_treatment_enabled": True,
                    "bridge_enabled": False,
                    "selected_legacy_rules_suppressed": True,
                    "diagnostic_counters": {},
                    "suppressed_selected_rule_ids": [],
                }
            },
        )
        cand = _source_file_obj("cand_struct_1", "pandaroot", "cand/file_1.cxx")
        contribution = D3StructuredContribution(
            candidates=[cand],
            bridged_candidates=[],
            candidate_provenance=[],
            reachability_receipts=[],
            bridge_receipts=[],
            diagnostic_counters={},
        )
        with patch(
            "panda_agent.retrieval.build_structured_contribution_from_storage",
            return_value=contribution,
        ):
            res = retriever.retrieve("Synthetic unbridged test", plan, d3_config=config)

        disp = res["d3_experiment"]["displacement_diagnostics"]
        self.assertEqual(disp["bridged_candidate_count"], 0)
        self.assertEqual(disp["graph_candidates_displaced_by_prefix"], 0)
        self.assertEqual(disp["displaced_object_ids"], [])
        self.assertEqual(disp["bridged_candidate_ids"], [])
        self.assertEqual(disp["deduplicated_overlap_count"], 0)

    def test_zero_bridge_exact_equivalence(self):
        """When bridge produces zero candidates, STRUCTURED_BRIDGED is identical to STRUCTURED_UNBRIDGED."""
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
            [], [], [],
            SimpleNamespace(
                text=question, raw_question=question, components=[],
                excluded_component_classes=[], as_dict=lambda: {},
            ),
        )
        retriever._dense = lambda *args: []
        retriever._sparse = lambda *args: []
        retriever._paper = lambda *args: []
        retriever._workflow = lambda *args: []
        ordinary_graph = [_source_file_obj(f"ord_graph_{i}", "pandaroot", f"ord/file_{i}.cxx") for i in range(5)]
        retriever._graph = lambda *args: list(ordinary_graph)

        unbridged_config = D3_5ExperimentConfig.for_arm(D3_5Arm.STRUCTURED_UNBRIDGED)
        bridged_config = D3_5ExperimentConfig.for_arm(D3_5Arm.STRUCTURED_BRIDGED)

        plan_unbridged = RetrievalPlan(
            intent="api", target_repositories=["pandaroot"], resolved_versions={"pandaroot": "locked"},
            concepts=[], symbols=[], concept_scopes={}, source_budgets={"code": 1.0}, required_source_types=[],
            analysis_diagnostics={
                "d3_experiment": {
                    "d3_arm": "STRUCTURED_UNBRIDGED", "selected_rule_ids": list(D3_5_SELECTED_RULE_IDS),
                    "structured_treatment_enabled": True, "bridge_enabled": False, "selected_legacy_rules_suppressed": True,
                }
            },
        )
        plan_bridged = RetrievalPlan(
            intent="api", target_repositories=["pandaroot"], resolved_versions={"pandaroot": "locked"},
            concepts=[], symbols=[], concept_scopes={}, source_budgets={"code": 1.0}, required_source_types=[],
            analysis_diagnostics={
                "d3_experiment": {
                    "d3_arm": "STRUCTURED_BRIDGED", "selected_rule_ids": list(D3_5_SELECTED_RULE_IDS),
                    "structured_treatment_enabled": True, "bridge_enabled": True, "selected_legacy_rules_suppressed": True,
                }
            },
        )

        cand = _source_file_obj("cand_baseline", "pandaroot", "cand/baseline.cxx")
        contribution_zero_bridge = D3StructuredContribution(
            candidates=[cand],
            bridged_candidates=[],
            candidate_provenance=[],
            reachability_receipts=[],
            bridge_receipts=[],
            diagnostic_counters={},
        )

        with patch(
            "panda_agent.retrieval.build_structured_contribution_from_storage",
            return_value=contribution_zero_bridge,
        ):
            res_unbridged = retriever.retrieve("Equivalence query", plan_unbridged, d3_config=unbridged_config)
            res_bridged = retriever.retrieve("Equivalence query", plan_bridged, d3_config=bridged_config)

        # Final evidence matches exactly in content and order
        unbridged_ev_ids = [e["object_id"] for e in res_unbridged["evidence"]]
        bridged_ev_ids = [e["object_id"] for e in res_bridged["evidence"]]
        self.assertEqual(unbridged_ev_ids, bridged_ev_ids)

    def test_additive_bridged_and_displacement_against_unbridged_baseline(self):
        """STRUCTURED_BRIDGED is unbridged baseline + bridged candidates, and displacement is measured against unbridged baseline."""
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
            [], [], [],
            SimpleNamespace(
                text=question, raw_question=question, components=[],
                excluded_component_classes=[], as_dict=lambda: {},
            ),
        )
        retriever._dense = lambda *args: []
        retriever._sparse = lambda *args: []
        retriever._paper = lambda *args: []
        retriever._workflow = lambda *args: []
        ordinary_graph = [_source_file_obj(f"ord_graph_{i}", "pandaroot", f"ord/file_{i}.cxx") for i in range(5)]
        retriever._graph = lambda *args: list(ordinary_graph)

        config = D3_5ExperimentConfig.for_arm(D3_5Arm.STRUCTURED_BRIDGED)
        plan = RetrievalPlan(
            intent="api", target_repositories=["pandaroot"], resolved_versions={"pandaroot": "locked"},
            concepts=[], symbols=[], concept_scopes={}, source_budgets={"code": 1.0}, required_source_types=[],
            analysis_diagnostics={
                "d3_experiment": {
                    "d3_arm": "STRUCTURED_BRIDGED", "selected_rule_ids": list(D3_5_SELECTED_RULE_IDS),
                    "structured_treatment_enabled": True, "bridge_enabled": True, "selected_legacy_rules_suppressed": True,
                }
            },
        )

        unbridged_cand = _source_file_obj("cand_unbridged_1", "pandaroot", "unbridged/cand_1.cxx")
        bridged_cand = _source_file_obj("cand_bridged_1", "pandaroot", "bridged/cand_1.cxx")

        contribution = D3StructuredContribution(
            candidates=[unbridged_cand],
            bridged_candidates=[bridged_cand],
            candidate_provenance=[],
            reachability_receipts=[],
            bridge_receipts=[],
            diagnostic_counters={},
        )

        with patch(
            "panda_agent.retrieval.build_structured_contribution_from_storage",
            return_value=contribution,
        ):
            res = retriever.retrieve("Additive query", plan, d3_config=config)

        disp = res["d3_experiment"]["displacement_diagnostics"]
        # unbridged_graph has: [cand_unbridged_1, ord_graph_0, ord_graph_1, ord_graph_2, ord_graph_3] (5 items)
        # final graph has: [cand_bridged_1, cand_unbridged_1, ord_graph_0, ord_graph_1, ord_graph_2] (5 items)
        # displaced item relative to unbridged baseline is ord_graph_3
        self.assertEqual(disp["bridged_candidate_count"], 1)
        self.assertEqual(disp["graph_candidates_before_bridge"], 5)
        self.assertEqual(disp["graph_candidates_after_bridge"], 5)
        self.assertEqual(disp["graph_candidates_displaced_by_prefix"], 1)
        self.assertEqual(disp["displaced_object_ids"], ["ord_graph_3"])
        self.assertEqual(disp["bridged_candidate_ids"], ["cand_bridged_1"])


class D3_5_ComprehensiveEdgeCasesTests(unittest.TestCase):
    def test_workflow_step_traversal_and_participants(self):
        wf_node = _gov_object("workflow.pandaroot.lmd_reconstruction", obj_type="workflow")
        subsys_node = _gov_object("subsystem.luminosityfit.panda_data_io", obj_type="subsystem")
        source_file = _source_file_obj("src_lmd", "pandaroot", "detectors/lmd/LmdQA/PndLmdTrackQ.cxx")
        steps = [
            {
                "workflow_id": "workflow.pandaroot.lmd_reconstruction",
                "step_id": "step_001",
                "name": "lmd_qa_step",
                "review_status": "accepted",
                "payload": {
                    "entrypoint_object_id": "subsystem.luminosityfit.panda_data_io",
                    "inputs": [],
                    "outputs": [],
                    "evidence_paths": ["detectors/lmd/LmdQA/PndLmdTrackQ.cxx"],
                    "evidence_source_ids": ["pandaroot"],
                },
            }
        ]
        reader = _MockGraphReader(
            rows=[wf_node, subsys_node],
            workflow_steps=steps,
            source_files=[source_file],
        )
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("workflow.pandaroot.lmd_reconstruction", "governed_id", "workflow.pandaroot.lmd_reconstruction",
                             RESOLVED_UNIQUE, matched_object_id="workflow.pandaroot.lmd_reconstruction",
                             canonical_object_id="workflow.pandaroot.lmd_reconstruction",
                             evidence=[_d2_evidence("G", "governed_id", "workflow.pandaroot.lmd_reconstruction")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Test workflow traversal", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        cand_ids = [c["object_id"] for c in result.candidates]
        self.assertIn("subsystem.luminosityfit.panda_data_io", cand_ids)
        bridged_ids = [c["object_id"] for c in result.bridged_candidates]
        self.assertIn("src_lmd", bridged_ids)
        wf_receipts = [
            r for r in result.reachability_receipts
            if "WORKFLOW_STEP" in r["structural_path"]["transition_types"]
        ]
        self.assertTrue(len(wf_receipts) > 0)
        self.assertEqual(wf_receipts[0]["structural_path"]["workflow_ids"], ["workflow.pandaroot.lmd_reconstruction"])

    def test_relation_and_workflow_mutual_exclusion_and_path_budget(self):
        root = _gov_object("data_product.restgas.event_poca", parent_id="data_product.restgas.boost_root", obj_type="data_product")
        parent = _gov_object("data_product.restgas.boost_root", obj_type="data_product")
        rel_target = _gov_object("workflow.restgas.first_pass_poca", obj_type="workflow")
        wf_target = _gov_object("workflow.restgas.second_pass_pid", obj_type="workflow")
        relations = [
            {
                "edge_id": "rel_edge_1",
                "subject_id": "workflow.restgas.first_pass_poca",
                "predicate": "PRODUCES",
                "object_id": "data_product.restgas.boost_root",
                "review_status": "accepted",
                "payload": {},
            }
        ]
        steps = [
            {
                "workflow_id": "workflow.two_pass",
                "step_id": "step_2",
                "name": "second_pass",
                "review_status": "accepted",
                "payload": {
                    "entrypoint_object_id": "workflow.restgas.second_pass_pid",
                    "inputs": ["data_product.restgas.boost_root"],
                },
            }
        ]
        reader = _MockGraphReader(
            rows=[root, parent, rel_target, wf_target],
            relations=relations,
            workflow_steps=steps,
        )
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("event_poca", "governed_id", "data_product.restgas.event_poca",
                             RESOLVED_UNIQUE, matched_object_id="data_product.restgas.event_poca",
                             canonical_object_id="data_product.restgas.event_poca",
                             evidence=[_d2_evidence("G", "governed_id", "data_product.restgas.event_poca")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Test mutual exclusion", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        for r in result.reachability_receipts:
            types = r["structural_path"]["transition_types"]
            # Budget consumed cannot exceed 2
            self.assertLessEqual(r["budget_consumed"], 2)
            # Cannot contain both ACCEPTED_RELATION and WORKFLOW_STEP on same path
            self.assertFalse("ACCEPTED_RELATION" in types and "WORKFLOW_STEP" in types)

    def test_structural_cap_32_and_budget_exhaustion(self):
        root = _gov_object("root_seed", obj_type="workflow")
        # 40 relation neighbors
        nodes = [root]
        relations = []
        for i in range(40):
            nid = f"neighbor_{i}"
            nodes.append(_gov_object(nid, obj_type="data_product"))
            relations.append({
                "edge_id": f"edge_{i}",
                "subject_id": "root_seed",
                "predicate": "PRODUCES",
                "object_id": nid,
                "review_status": "accepted",
                "payload": {},
            })
        reader = _MockGraphReader(rows=nodes, relations=relations)
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("root_seed", "governed_id", "root_seed",
                             RESOLVED_UNIQUE, matched_object_id="root_seed",
                             canonical_object_id="root_seed",
                             evidence=[_d2_evidence("G", "governed_id", "root_seed")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Test cap 32", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        reached = [r for r in result.reachability_receipts if r["reachability_status"] == "REACHED"]
        exhausted = [
            r for r in result.reachability_receipts
            if r["reachability_status"] == "TRAVERSAL_BUDGET_EXHAUSTED"
        ]
        self.assertLessEqual(len(reached), GLOBAL_REACHABLE_STRUCTURE_CAP)
        self.assertTrue(len(exhausted) > 0)

    def test_missing_and_standard_failures(self):
        # 1. No eligible seeds
        receipt_empty = D2ResolutionReceipt(resolutions=[])
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        reader = _MockGraphReader()
        result1 = build_structured_contribution(
            "No seed test", plan, resolver=_MockResolver(receipt_empty), graph_reader=reader, bridge_enabled=True
        )
        self.assertEqual(len(result1.reachability_receipts), 1)
        self.assertEqual(result1.reachability_receipts[0]["reachability_status"], "NO_ELIGIBLE_STRUCTURED_SEED")

        # 2. Reached origin has no provenance -> GOVERNED_PROVENANCE_NOT_FOUND
        node = _gov_object("empty_gov", obj_type="workflow")
        reader2 = _MockGraphReader(rows=[node])
        receipt_seed = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("empty_gov", "governed_id", "empty_gov",
                             RESOLVED_UNIQUE, matched_object_id="empty_gov",
                             canonical_object_id="empty_gov",
                             evidence=[_d2_evidence("G", "governed_id", "empty_gov")]),
            ]
        )
        result2 = build_structured_contribution(
            "No prov test", plan, resolver=_MockResolver(receipt_seed), graph_reader=reader2, bridge_enabled=True
        )
        b_statuses = [b["bridge_status"] for b in result2.bridge_receipts]
        self.assertIn("GOVERNED_PROVENANCE_NOT_FOUND", b_statuses)

        # 3. Path not found in corpus -> PROVENANCE_SOURCE_OBJECT_NOT_FOUND
        node_with_path = _gov_object("gov_with_path", obj_type="workflow")
        node_with_path["metadata"] = {
            "evidence_paths": ["nonexistent/file.cxx"],
            "evidence_source_ids": ["pandaroot"],
        }
        reader3 = _MockGraphReader(rows=[node_with_path])
        receipt3 = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov_with_path", "governed_id", "gov_with_path",
                             RESOLVED_UNIQUE, matched_object_id="gov_with_path",
                             canonical_object_id="gov_with_path",
                             evidence=[_d2_evidence("G", "governed_id", "gov_with_path")]),
            ]
        )
        result3 = build_structured_contribution(
            "Path missing test", plan, resolver=_MockResolver(receipt3), graph_reader=reader3, bridge_enabled=True
        )
        b_statuses3 = [b["bridge_status"] for b in result3.bridge_receipts]
        self.assertIn("PROVENANCE_SOURCE_OBJECT_NOT_FOUND", b_statuses3)

    def test_ambiguous_path_retains_all_matched_ids(self):
        node = _gov_object("gov_ambig", obj_type="workflow")
        node["metadata"] = {
            "evidence_paths": ["common/util.cxx"],
            "evidence_source_ids": ["pandaroot"],
        }
        src1 = _source_file_obj("src_file_a", "pandaroot", "common/util.cxx")
        src2 = _source_file_obj("src_file_b", "pandaroot", "common/util.cxx")
        reader = _MockGraphReader(rows=[node], source_files=[src1, src2])
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov_ambig", "governed_id", "gov_ambig",
                             RESOLVED_UNIQUE, matched_object_id="gov_ambig",
                             canonical_object_id="gov_ambig",
                             evidence=[_d2_evidence("G", "governed_id", "gov_ambig")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Ambig test", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        ambig_receipts = [b for b in result.bridge_receipts if b["bridge_status"] == "PROVENANCE_SOURCE_OBJECT_AMBIGUOUS"]
        self.assertEqual(len(ambig_receipts), 1)
        ambig = ambig_receipts[0]
        matched_ids = ambig["lookup_locator"]["matched_object_ids"]
        self.assertIn("src_file_a", matched_ids)
        self.assertIn("src_file_b", matched_ids)
        self.assertEqual(len(result.bridged_candidates), 0)

    def test_missing_evidence_source_ids_fails_closed(self):
        """Missing evidence_source_ids on evidence_paths fails closed (Defect 4)."""
        node_no_src = _gov_object("gov_no_src", obj_type="workflow")
        node_no_src["metadata"] = {
            "evidence_paths": ["detectors/lmd/LmdQA/PndLmdTrackQ.cxx"],
            # missing evidence_source_ids
        }
        src_file = _source_file_obj("src_lmd_id", "pandaroot", "detectors/lmd/LmdQA/PndLmdTrackQ.cxx")
        reader = _MockGraphReader(rows=[node_no_src], source_files=[src_file])
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov_no_src", "governed_id", "gov_no_src",
                             RESOLVED_UNIQUE, matched_object_id="gov_no_src",
                             canonical_object_id="gov_no_src",
                             evidence=[_d2_evidence("G", "governed_id", "gov_no_src")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Missing source test", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        path_receipts = [b for b in result.bridge_receipts if b["evidence_field_used"] == "evidence_paths"]
        self.assertEqual(len(path_receipts), 1)
        self.assertEqual(path_receipts[0]["bridge_status"], "GOVERNED_PROVENANCE_INVALID")
        self.assertIn("evidence path lacks explicit governed source qualification", path_receipts[0]["reason_included"])
        self.assertEqual(len(result.bridged_candidates), 0)

    def test_unauthorized_source_and_version_conflict_fail_closed(self):
        # 1. Unauthorized source does NOT fallback to plan targets
        node_unauth = _gov_object("gov_unauth", obj_type="workflow")
        node_unauth["metadata"] = {
            "evidence_paths": ["file.cxx"],
            "evidence_source_ids": ["unauthorized_repo"],
        }
        reader1 = _MockGraphReader(rows=[node_unauth])
        receipt1 = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov_unauth", "governed_id", "gov_unauth",
                             RESOLVED_UNIQUE, matched_object_id="gov_unauth",
                             canonical_object_id="gov_unauth",
                             evidence=[_d2_evidence("G", "governed_id", "gov_unauth")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result1 = build_structured_contribution(
            "Unauth source test", plan, resolver=_MockResolver(receipt1), graph_reader=reader1, bridge_enabled=True
        )
        statuses1 = [b["bridge_status"] for b in result1.bridge_receipts]
        self.assertIn("VERSION_SCOPE_CONFLICT", statuses1)
        self.assertEqual(len(result1.bridged_candidates), 0)

        # 2. Conflicting version fails closed
        node_ver = _gov_object("gov_ver", obj_type="workflow")
        node_ver["metadata"] = {
            "evidence_paths": ["file.cxx"],
            "evidence_source_ids": ["pandaroot"],
            "source_version_ids": ["pandaroot@wrong_ver"],
        }
        reader2 = _MockGraphReader(rows=[node_ver])
        receipt2 = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov_ver", "governed_id", "gov_ver",
                             RESOLVED_UNIQUE, matched_object_id="gov_ver",
                             canonical_object_id="gov_ver",
                             evidence=[_d2_evidence("G", "governed_id", "gov_ver")]),
            ]
        )
        result2 = build_structured_contribution(
            "Version conflict test", plan, resolver=_MockResolver(receipt2), graph_reader=reader2, bridge_enabled=True
        )
        statuses2 = [b["bridge_status"] for b in result2.bridge_receipts]
        self.assertIn("VERSION_SCOPE_CONFLICT", statuses2)

    def test_domain_semantic_evidence_object_rejected(self):
        node = _gov_object("gov_anchor", obj_type="workflow")
        node["metadata"] = {
            "evidence_object_ids": ["workflow.pandaroot.lmd_reconstruction"],
        }
        domain_anchor = _gov_object("workflow.pandaroot.lmd_reconstruction", source_id="curated_panda_domain", obj_type="workflow")
        reader = _MockGraphReader(rows=[node, domain_anchor])
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov_anchor", "governed_id", "gov_anchor",
                             RESOLVED_UNIQUE, matched_object_id="gov_anchor",
                             canonical_object_id="gov_anchor",
                             evidence=[_d2_evidence("G", "governed_id", "gov_anchor")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Domain anchor reject test", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        b_receipts = [b for b in result.bridge_receipts if b["evidence_field_used"] == "evidence_object_ids"]
        self.assertEqual(len(b_receipts), 1)
        self.assertEqual(b_receipts[0]["bridge_status"], "GOVERNED_PROVENANCE_INVALID")
        self.assertIn("curated domain semantic object rejected as bridged candidate (remains anchor only)", b_receipts[0]["reason_included"])
        self.assertEqual(len(result.bridged_candidates), 0)

    def test_deduplication_before_cap_does_not_false_rank_out(self):
        root = _gov_object("gov_root", obj_type="workflow")
        # 25 nodes referencing the exact SAME file
        nodes = [root]
        relations = []
        for i in range(25):
            nid = f"child_{i}"
            nodes.append(_gov_object(nid, obj_type="data_product"))
            relations.append({
                "edge_id": f"rel_{i}",
                "subject_id": "gov_root",
                "predicate": "PRODUCES",
                "object_id": nid,
                "review_status": "accepted",
                "payload": {
                    "evidence_paths": ["shared/target_file.cxx"],
                    "evidence_source_ids": ["pandaroot"],
                },
            })
        shared_file = _source_file_obj("shared_src_id", "pandaroot", "shared/target_file.cxx")
        reader = _MockGraphReader(rows=nodes, relations=relations, source_files=[shared_file])
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov_root", "governed_id", "gov_root",
                             RESOLVED_UNIQUE, matched_object_id="gov_root",
                             canonical_object_id="gov_root",
                             evidence=[_d2_evidence("G", "governed_id", "gov_root")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Dedup test", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        self.assertEqual(len(result.bridged_candidates), 1)
        self.assertEqual(result.diagnostic_counters["bridged_candidate_ranked_out_count"], 0)

    def test_forked_from_explicit_endpoint_and_version_validation(self):
        repo_restgas = _gov_object(
            "repository.restgas_determination.oct19",
            source_id="restgas_determination",
            source_version_id="11f1edc49dcbaeb61d707491a6d3bbec390fcd42",
            obj_type="repository_version",
        )
        repo_pandaroot = _gov_object(
            "repository.pandaroot.oct19",
            source_id="pandaroot",
            source_version_id="18c09e91100db27867ded30e708b4dae95bd8357",
            obj_type="repository_version",
        )
        rel = {
            "edge_id": "e_fork",
            "subject_id": "repository.restgas_determination.oct19",
            "predicate": "FORKED_FROM",
            "object_id": "repository.pandaroot.oct19",
            "review_status": "accepted",
            "payload": {
                "source_version_ids": [
                    "restgas_determination@11f1edc49dcbaeb61d707491a6d3bbec390fcd42",
                    "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
                ]
            },
        }
        reader = _MockGraphReader(rows=[repo_restgas, repo_pandaroot], relations=[rel])
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("restgas", "governed_id", "repository.restgas_determination.oct19",
                             RESOLVED_UNIQUE, matched_object_id="repository.restgas_determination.oct19",
                             canonical_object_id="repository.restgas_determination.oct19",
                             evidence=[_d2_evidence("G", "governed_id", "repository.restgas_determination.oct19")]),
            ]
        )
        # 1. Version conflict rejects FORKED_FROM
        plan_bad_ver = {
            "target_repositories": ["restgas_determination", "pandaroot"],
            "resolved_versions": {"pandaroot": "different_hash"},
        }
        result_bad = build_structured_contribution(
            "Fork bad ver", plan_bad_ver, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        cand_ids_bad = [c["object_id"] for c in result_bad.candidates]
        self.assertNotIn("repository.pandaroot.oct19", cand_ids_bad)

        # 2. Matching versions accepts FORKED_FROM
        plan_good = {
            "target_repositories": ["restgas_determination", "pandaroot"],
            "resolved_versions": {
                "restgas_determination": "11f1edc49dcbaeb61d707491a6d3bbec390fcd42",
                "pandaroot": "18c09e91100db27867ded30e708b4dae95bd8357",
            },
        }
        result_good = build_structured_contribution(
            "Fork good ver", plan_good, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        cand_ids_good = [c["object_id"] for c in result_good.candidates]
        self.assertIn("repository.pandaroot.oct19", cand_ids_good)

    def test_sql_reader_query_mechanics(self):
        class _MockExecution:
            def fetchall(self):
                return [
                    (
                        "test_obj_1",
                        "pandaroot",
                        "pandaroot@locked",
                        "source_file",
                        "test_file.cxx",
                        "code",
                        "primary",
                        {"path": "src/test_file.cxx"},
                        {},
                        "src/test_file.cxx",
                    )
                ]

        class _MockConn:
            def __init__(self):
                self.query = None
                self.params = None
            def execute(self, q, p):
                self.query = q
                self.params = p
                return _MockExecution()
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass

        class _MockStorage:
            def __init__(self, conn):
                self.conn = conn
            def connect(self):
                return self.conn

        conn = _MockConn()
        storage = _MockStorage(conn)
        reader = PostgresD3StructuredGraphReader(storage)
        res = reader.find_source_objects_by_path("pandaroot", "src/test_file.cxx")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["object_id"], "test_obj_1")
        self.assertIn("source_id=%s", conn.query)


    def test_d3_5_arms_keep_other_five_rules_active_in_background(self):
        """Defect 1: D3.5 suppresses only 2 rules, keeping the other 5 historical rules active as background expansions."""
        project_root = Path(__file__).resolve().parents[2]
        from panda_agent.config import load_query_expansions
        rules = load_query_expansions(project_root / "configs" / "query_expansions.yaml").rules
        question = " || ".join(rule.triggers[0] for rule in rules)
        all_rule_ids = {rule.rule_id for rule in rules}

        for arm in (D3_5Arm.ABLATION, D3_5Arm.STRUCTURED_UNBRIDGED, D3_5Arm.STRUCTURED_BRIDGED):
            config = D3_5ExperimentConfig.for_arm(arm)
            decision = select_matching_query_expansions(question, rules, config)
            # Only the 2 D3.5 rules are suppressed
            self.assertEqual(set(decision.suppressed_selected_rule_ids), set(D3_5_SELECTED_RULE_IDS))
            # The remaining 52 rules (including the other 5 historical D3 rules) remain active
            other_five_historical = set(SELECTED_D3_RULE_IDS) - set(D3_5_SELECTED_RULE_IDS)
            active_ids = {r.rule_id for r in decision.active_matching_rules}
            for hist_rule_id in other_five_historical:
                self.assertIn(hist_rule_id, active_ids)
            self.assertEqual(active_ids, all_rule_ids - set(D3_5_SELECTED_RULE_IDS))

    def test_unbridged_baseline_preserves_unbounded_unique_and_ambiguous_seeds(self):
        """Defect 2: unbridged structured baseline admits >8 seeds and all Tier-D ambiguity candidates without cap."""
        # 12 unique G seeds + 9 ambiguous Tier-D candidates
        resolutions = [
            D2Resolution(f"G_{i}", "governed_id", f"G_{i}", RESOLVED_UNIQUE,
                         matched_object_id=f"g_obj_{i}", canonical_object_id=f"canon_g_{i}",
                         evidence=[_d2_evidence("G", "governed_id", f"g_obj_{i}")])
            for i in range(12)
        ]
        resolutions.append(
            D2Resolution("Amb_9", "descriptive", "Amb_9", AMBIGUOUS,
                         candidates=[{"object_id": f"amb_obj_{i}", "tier": "D"} for i in range(9)])
        )
        receipt = D2ResolutionReceipt(resolutions=resolutions)
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}

        # Unbridged seed derivation admits all 12 + 9 = 21 seeds
        unbridged_seeds, unb_excluded, _ = derive_unbridged_structured_seeds(receipt, "Test query", plan)
        self.assertEqual(len(unbridged_seeds), 21)

        # Bridge seed derivation admits exactly 8 (first 8 G seeds, 0 ambiguous)
        bridge_seeds, br_excluded, _ = derive_d3_5_bridge_seeds(receipt, "Test query", plan)
        self.assertEqual(len(bridge_seeds), 8)
        self.assertTrue(any(e.get("reason") == "AMBIGUITY_SET_EXCEEDS_SAFE_SEED_BUDGET" for e in br_excluded))

    def test_evidence_object_ids_does_not_require_evidence_source_ids(self):
        """Defect 4: evidence_object_ids does not require explicit evidence_source_ids for lookup."""
        gov_node = _gov_object("gov_obj_src", obj_type="workflow")
        gov_node["metadata"] = {
            "evidence_object_ids": ["source_code_target_1"],
            # note: no evidence_source_ids specified
        }
        target_obj = _source_file_obj("source_code_target_1", "pandaroot", "src/target.cxx")
        reader = _MockGraphReader(rows=[gov_node, target_obj])
        receipt = D2ResolutionReceipt(
            resolutions=[
                D2Resolution("gov_obj_src", "governed_id", "gov_obj_src",
                             RESOLVED_UNIQUE, matched_object_id="gov_obj_src",
                             canonical_object_id="gov_obj_src",
                             evidence=[_d2_evidence("G", "governed_id", "gov_obj_src")]),
            ]
        )
        plan = {"target_repositories": ["pandaroot"], "resolved_versions": {"pandaroot": "locked"}}
        result = build_structured_contribution(
            "Evidence object test", plan, resolver=_MockResolver(receipt), graph_reader=reader, bridge_enabled=True
        )
        self.assertEqual(len(result.bridged_candidates), 1)
        self.assertEqual(result.bridged_candidates[0]["object_id"], "source_code_target_1")
        obj_receipts = [b for b in result.bridge_receipts if b["evidence_field_used"] == "evidence_object_ids"]
        self.assertEqual(len(obj_receipts), 1)
        self.assertEqual(obj_receipts[0]["bridge_status"], "BRIDGED_CANDIDATE_INJECTED")


if __name__ == "__main__":
    unittest.main()
