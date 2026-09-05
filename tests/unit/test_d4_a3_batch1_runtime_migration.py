"""Unit tests for D4-A3 First-Batch Runtime Migration.

Covers all 29 verification requirements from the D4-A3 specification:
- Config: 1-6
- Production policy: 7-10
- Selectivity: 11-15
- Admission: 16-21
- Runtime integration: 22-26
- Anti-shortcut: 27-29
- Parity against frozen evaluation algorithms
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_EVAL_DIR = _REPO_ROOT / "evaluation"
if str(_EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_DIR))

import pytest
import yaml

from panda_agent.config import load_query_expansions
from panda_agent.d3_structured import (
    DEFAULT_ADMISSION_K,
    ELIGIBLE_BRIDGE_STATUSES,
    MIN_PRIMARY_SCORE,
    PER_ORIGIN_CAP,
    SELECTIVITY_CAP,
    SELECTIVITY_POLICY_VERSION,
    D3Arm,
    D3ExperimentConfig,
    D3StructuredContribution,
    build_candidate_payload_registry,
    build_eligible_bridge_candidates,
    build_treatment_pool,
    exact_normalize,
    plan_scope_set,
    query_token_set,
    reservable_bridge,
    select_structured_candidates_v2,
    symbol_exact_match,
    tokenize,
)
from panda_agent.models import RetrievalPlan
from panda_agent.retrieval import Retriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "configs" / "query_expansions.yaml"


# ============================================================================
# 1. Config Verification (Req 1-6)
# ============================================================================

class TestBatch1ConfigMigration:
    """Requirements 1-6: Config migration invariants."""

    @pytest.fixture(autouse=True)
    def setup_config(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.raw_data = yaml.safe_load(f)
        self.qe = load_query_expansions(CONFIG_PATH)
        self.rules_by_id = {r.rule_id: r for r in self.qe.rules}
        self.raw_rules_by_id = {r["rule_id"]: r for r in self.raw_data["rules"]}

    def test_req1_exactly_batch1_rules_marked_migrated(self):
        """Req 1: Exactly the two Batch-1 rules have structured_replacement enabled."""
        migrated_ids = [r.rule_id for r in self.qe.rules if r.structured_replacement]
        assert sorted(migrated_ids) == ["event_poca_handoff", "restgas_profile_workflow"]

    def test_req2_event_poca_handoff_symbols_empty(self):
        """Req 2: event_poca_handoff fixed symbols are empty."""
        rule = self.rules_by_id["event_poca_handoff"]
        assert rule.symbols == []
        former_symbols = {
            "macro/target/ana_dpm.C",
            "macro/target/prod_aod_complete.C",
            "POCA_VERTEX_FILE",
            "PndPidCorrelator",
        }
        assert not any(sym in former_symbols for sym in rule.symbols)

    def test_req3_event_poca_handoff_page_hints_absent(self):
        """Req 3: event_poca_handoff fixed li_2026 [131, 138] hint is absent."""
        rule = self.rules_by_id["event_poca_handoff"]
        assert "li_2026" not in rule.paper_page_hints
        assert rule.paper_page_hints == {}

    def test_req4_restgas_profile_workflow_symbols_empty(self):
        """Req 4: restgas_profile_workflow fixed symbols are empty."""
        rule = self.rules_by_id["restgas_profile_workflow"]
        assert rule.symbols == []
        former_symbols = {
            "pgenerators/Target/PndTargetGenerator.cxx",
            "macro/target/prod_sim_hvmaps.C",
            "macro/target/reco_complete.C",
            "macro/target/ana_complete.C",
            "macro/target/correction/efficiency_correction_2.C",
        }
        assert not any(sym in former_symbols for sym in rule.symbols)

    def test_req5_exact_triggers_repos_concepts_preserved(self):
        """Req 5: Both rules retain exact triggers, repositories, and concepts."""
        poca = self.rules_by_id["event_poca_handoff"]
        assert poca.triggers == ["event_poca", "poca_vertex_file", "second-pass pid", "第二遍 pid"]
        assert "event_poca" in poca.triggers
        assert "poca_vertex_file" in poca.triggers
        assert len(poca.triggers) == 4
        assert poca.repositories == ["restgas_determination", "pandaroot"]
        assert poca.concepts == ["event POCA handoff", "event-aligned second-pass propagation"]

        restgas = self.rules_by_id["restgas_profile_workflow"]
        assert restgas.triggers == ["restgas_profile", "restgas profile", "corrected rho", "修正后的 rho"]
        assert "restgas_profile" in restgas.triggers
        assert "corrected rho" in restgas.triggers
        assert len(restgas.triggers) == 4
        assert restgas.repositories == ["restgas_determination", "pandaroot"]
        assert restgas.concepts == ["distributed target generation", "longitudinal profile correction"]

    def test_req6_non_batch1_rules_unchanged(self):
        """Req 6: Non-Batch1 rules remain semantically unchanged."""
        for rule in self.qe.rules:
            if rule.rule_id not in {"event_poca_handoff", "restgas_profile_workflow"}:
                assert rule.structured_replacement is False
        # Check a representative non-migrated rule retains symbols
        assert len(self.rules_by_id["pid_two_pass_files"].symbols) > 0
        before = yaml.safe_load(subprocess.check_output(
            ["git", "show", "8c0971f20f9a2b2680451e3123fa1d95325816bc:configs/query_expansions.yaml"],
            cwd=PROJECT_ROOT, encoding="utf-8",
        ))
        for rule in before["rules"]:
            if rule["rule_id"] not in {"event_poca_handoff", "restgas_profile_workflow"}:
                assert self.raw_rules_by_id[rule["rule_id"]] == rule
        assert [r["rule_id"] for r in before["rules"]] == [r["rule_id"] for r in self.raw_data["rules"]]


# ============================================================================
# 2. Production Policy and Activation (Req 7-10)
# ============================================================================

class TestProductionPolicyAndActivation:
    """Requirements 7-10: Production policy and activation semantics."""

    def _make_retriever(self):
        retriever = object.__new__(Retriever)
        retriever.project_root = PROJECT_ROOT
        retriever.policies = SimpleNamespace(
            candidate_pool_per_channel=10,
            max_relation_hops=2,
            final_evidence_limit=3,
        )
        retriever.query_expansions = load_query_expansions(CONFIG_PATH)
        retriever.context_sources = []
        retriever.storage = object()
        retriever.fixed_versions = {
            "luminosityfit": "a" * 40,
            "pandaroot": "b" * 40,
            "restgas_determination": "c" * 40,
        }
        retriever.vertex = SimpleNamespace(
            generate_json=MagicMock(return_value={"ranked_object_ids": []})
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

    def test_req7_non_migrated_matched_rules_do_not_activate(self):
        """Req 7: Non-migrated matched rules do not activate structured replacement."""
        retriever = self._make_retriever()
        plan = retriever._preparse("where is pid_final.root used")
        assert "pid_two_pass_files" in plan.matched_expansion_rules
        assert plan.structured_replacement_rules == []

    def test_req8_migrated_rules_activate_automatically_default_mode(self):
        """Req 8: Migrated rules activate automatically in default mode."""
        retriever = self._make_retriever()
        plan = retriever._preparse("Where is event_poca defined?")
        assert "event_poca_handoff" in plan.matched_expansion_rules
        assert "event_poca_handoff" in plan.structured_replacement_rules

    def test_req9_no_explicit_d3_config_required(self):
        """Req 9: No explicit d3_config is required for activation."""
        retriever = self._make_retriever()
        plan = retriever._preparse("Where is event_poca defined?", d3_config=None)
        assert "event_poca_handoff" in plan.structured_replacement_rules
        assert plan.d3_experiment is None

    def test_req10_externally_supplied_plan_preserves_contract(self):
        """Req 10: Externally supplied plans preserve the validation contract."""
        retriever = self._make_retriever()
        # Supplying a plan with no migrated rules
        plan = RetrievalPlan(
            intent="installation",
            target_repositories=["pandaroot"],
            resolved_versions={"pandaroot": "b" * 40},
            concepts=[],
            symbols=[],
            concept_scopes={},
            source_budgets={"code": 1.0},
            required_source_types=[],
            analysis_diagnostics={"matched_expansion_rules": []},
        )
        with patch("panda_agent.retrieval.build_structured_contribution_from_storage") as mock_sc:
            result = retriever.retrieve("Generic question", plan=plan)
            mock_sc.assert_not_called()
            assert "structured_replacement" not in result


# ============================================================================
# 3. Selectivity Semantics (Req 11-15)
# ============================================================================

class TestSelectivityV2Semantics:
    """Requirements 11-15: Exact selectivity-v2 semantics."""

    def test_req11_caps_are_8_and_4(self):
        """Req 11: Caps are exactly 8 and 4, MIN_PRIMARY_SCORE is 1."""
        assert SELECTIVITY_CAP == 8
        assert PER_ORIGIN_CAP == 4
        assert MIN_PRIMARY_SCORE == 1
        assert SELECTIVITY_POLICY_VERSION == "d3_5_selectivity_v2"

    def test_req12_tokenizer_exact_match_ranking_semantics(self):
        """Req 12: Frozen tokenizer and boundary-aware exact matching are preserved."""
        assert tokenize("PndTargetGenerator.cxx") == {"pnd", "target", "generator", "cxx"}
        assert exact_normalize("pgenerators\\Target\\PndTargetGenerator.cxx") == "pgenerators/target/pndtargetgenerator.cxx"
        assert symbol_exact_match("PndTargetGenerator", "pgenerators/Target/PndTargetGenerator.cxx") is True
        assert symbol_exact_match("PndTargetGenerator", "pgenerators/Target/PndTargetGeneratorExtra.cxx") is False
        assert symbol_exact_match("event_poca", "event_poca.cxx") is True
        assert symbol_exact_match("event_poca", "sub_event_poca.cxx") is False

    def test_req13_source_scope_rejection_fail_closed(self):
        """Req 13: Source-scope rejection remains fail-closed."""
        plan = {"target_repositories": ["pandaroot"], "symbols": [], "concepts": []}
        candidates = [
            {
                "candidate_object_id": "c1",
                "source_id": "restgas_determination",  # out of scope
                "provenance_origin_ids": ["o1"],
                "locator_path": "foo/bar.C",
                "min_structural_distance_transitions": 1,
            },
            {
                "candidate_object_id": "c2",
                "source_id": "pandaroot",  # in scope
                "provenance_origin_ids": ["o1"],
                "locator_path": "foo/bar.C",
                "min_structural_distance_transitions": 1,
            },
        ]
        registry = {
            "c1": {"title": "bar", "text": "bar"},
            "c2": {"title": "bar", "text": "bar"},
        }
        res = select_structured_candidates_v2("bar", plan, candidates, registry)
        assert res["scope_rejected_candidate_count"] == 1
        assert "c1" not in res["selected_object_ids"]
        assert "c2" in res["selected_object_ids"]

    def test_req14_per_origin_ceiling_enforced(self):
        """Req 14: Per-origin ceiling is enforced at 4."""
        plan = {"target_repositories": ["pandaroot"], "symbols": [], "concepts": []}
        # 6 candidates from the same origin o1
        candidates = [
            {
                "candidate_object_id": f"c_{i}",
                "source_id": "pandaroot",
                "provenance_origin_ids": ["o1"],
                "locator_path": f"src/code_{i}.C",
                "min_structural_distance_transitions": i,
            }
            for i in range(6)
        ]
        registry = {
            f"c_{i}": {"title": f"code_{i}", "text": "code"}
            for i in range(6)
        }
        res = select_structured_candidates_v2("code", plan, candidates, registry)
        assert res["selected_bridge_candidate_count"] == 4
        assert res["origin_capped_out_count"] == 2

    def test_req15_selectivity_result_is_deterministic(self):
        """Req 15: Selectivity result is deterministic regardless of candidate input order."""
        plan = {"target_repositories": ["pandaroot"], "symbols": [], "concepts": []}
        candidates = [
            {
                "candidate_object_id": f"c_{i}",
                "source_id": "pandaroot",
                "provenance_origin_ids": [f"o_{i % 3}"],
                "locator_path": f"src/mod_{i}.C",
                "min_structural_distance_transitions": i,
            }
            for i in range(10)
        ]
        registry = {
            f"c_{i}": {"title": f"mod_{i}", "text": "sample text"}
            for i in range(10)
        }
        res1 = select_structured_candidates_v2("mod", plan, candidates, registry)
        res2 = select_structured_candidates_v2("mod", plan, list(reversed(candidates)), registry)
        assert res1["selected_object_ids"] == res2["selected_object_ids"]


# ============================================================================
# 4. Admission Semantics (Req 16-21)
# ============================================================================

class TestAdmissionK3Semantics:
    """Requirements 16-21: Exact K=3 bounded admission semantics."""

    def test_req16_k_is_3(self):
        """Req 16: Admission K is exactly 3."""
        assert DEFAULT_ADMISSION_K == 3

    def test_req17_pool_max_30(self):
        """Req 17: Treatment pool size <= 30."""
        baseline = [f"b_{i}" for i in range(30)]
        reservable = ["r_1", "r_2", "r_3", "r_4"]
        pool = build_treatment_pool(baseline, reservable, k=3)
        assert pool["pool_size"] == 30
        assert len(pool["treatment_pool_object_ids"]) == 30

    def test_req18_overlapping_candidates_not_double_admitted(self):
        """Req 18: Baseline-overlapping candidates are not double-admitted."""
        baseline = ["b_1", "b_2", "b_3"]
        v2_order = ["b_2", "r_1", "b_1", "r_2"]
        res = reservable_bridge(v2_order, baseline)
        assert res == ["r_1", "r_2"]

    def test_req19_reserved_displace_bottom_ordinary_only(self):
        """Req 19: Reserved candidates displace bottom ordinary candidates only."""
        baseline = [f"b_{i}" for i in range(30)]
        reservable = ["r_1", "r_2", "r_3"]
        pool = build_treatment_pool(baseline, reservable, k=3)
        # Top 27 baseline survive
        assert pool["treatment_pool_object_ids"][:27] == [f"b_{i}" for i in range(27)]
        # 3 reserved candidates appended
        assert pool["treatment_pool_object_ids"][27:] == ["r_1", "r_2", "r_3"]
        # Displaced are bottom 3 baseline
        assert pool["displaced_object_ids"] == ["b_27", "b_28", "b_29"]

    def test_req20_fewer_than_3_reservable(self):
        """Req 20: Fewer than 3 reservable candidates reserve only what exists."""
        baseline = [f"b_{i}" for i in range(30)]
        reservable = ["r_1"]
        pool = build_treatment_pool(baseline, reservable, k=3)
        assert pool["reserved_slot_count"] == 1
        assert pool["reserved_bridge_candidate_ids"] == ["r_1"]
        assert pool["displaced_object_ids"] == ["b_29"]
        assert len(pool["treatment_pool_object_ids"]) == 30

    def test_req21_zero_reservable_leaves_baseline_identical(self):
        """Req 21: Zero reservable candidates leaves pool identical to baseline."""
        baseline = [f"b_{i}" for i in range(30)]
        pool = build_treatment_pool(baseline, [], k=3)
        assert pool["treatment_pool_object_ids"] == baseline
        assert pool["displaced_object_ids"] == []
        assert pool["reserved_slot_count"] == 0


# ============================================================================
# 5. Runtime Integration (Req 22-26)
# ============================================================================

class TestRuntimeIntegration:
    """Requirements 22-26: Runtime integration into Retriever.retrieve()."""

    def test_real_analyzer_default_entry_and_generic_policy(self):
        from panda_agent.config import QueryExpansionRule, QueryExpansions
        from test_retrieval import FakeVertex

        retriever = self._setup_retriever_with_mocks()
        retriever.query_expansions = QueryExpansions(schema_version="1.0.0", rules=[QueryExpansionRule(
            rule_id="synthetic_policy", triggers=["module_alpha"],
            repositories=["pandaroot"], concepts=["alpha"], structured_replacement=True,
        )])
        retriever.fixed_refs = {repo: "dev" for repo in retriever.fixed_versions}
        retriever.web_version_tokens = set()
        retriever.policies.intents = {
            "algorithm_implementation": SimpleNamespace(source_budgets={"code": 1.0}, required_sources=[]),
        }
        prompts = []

        def generate(prompt, schema, **kwargs):
            payload = json.loads(prompt)
            prompts.append(payload)
            if payload.get("task") == "rerank_evidence":
                return {"ranked_object_ids": [c["object_id"] for c in payload["untrusted_candidates"]]}
            return FakeVertex().generate_json(prompt, schema, **kwargs)

        retriever.vertex.generate_json.side_effect = generate
        with patch("panda_agent.retrieval.build_structured_contribution_from_storage",
                   return_value=D3StructuredContribution()) as bridge:
            result = retriever.retrieve("Describe module_alpha")
        bridge.assert_called_once()
        plan = bridge.call_args.args[1]
        assert plan.analysis_diagnostics["matched_expansion_rules"] == ["synthetic_policy"]
        assert plan.analysis_diagnostics["structured_replacement_rules"] == ["synthetic_policy"]
        assert result["structured_replacement"]["active_migrated_rule_ids"] == ["synthetic_policy"]
        assert len(prompts) == 2
        assert sum(p.get("task") == "rerank_evidence" for p in prompts) == 1
        assert "structured_replacement_rules" not in json.dumps(prompts[0]["deterministic_context"])

    @pytest.mark.parametrize("diagnostics", [{}, {
        "matched_expansion_rules": ["pid_two_pass_files"],
        "structured_replacement_rules": ["pid_two_pass_files"],
    }])
    def test_normal_supplied_plan_cannot_enable_unmigrated_policy(self, diagnostics):
        retriever = self._setup_retriever_with_mocks()
        plan = RetrievalPlan(intent="usage", source_budgets={"code": 1.0}, analysis_diagnostics=diagnostics)
        with patch("panda_agent.retrieval.build_structured_contribution_from_storage") as bridge:
            retriever.retrieve("Explain pid_final.root", plan=plan)
        bridge.assert_not_called()

    def test_normal_supplied_plan_without_diagnostics_uses_current_policy(self):
        retriever = self._setup_retriever_with_mocks()
        plan = RetrievalPlan(intent="usage", source_budgets={"code": 1.0})
        with patch("panda_agent.retrieval.build_structured_contribution_from_storage",
                   return_value=D3StructuredContribution()) as bridge:
            retriever.retrieve("Explain event_poca", plan=plan)
        bridge.assert_called_once()

    def _setup_retriever_with_mocks(self):
        retriever = object.__new__(Retriever)
        retriever.project_root = PROJECT_ROOT
        retriever.policies = SimpleNamespace(
            candidate_pool_per_channel=10,
            max_relation_hops=2,
            final_evidence_limit=5,
        )
        retriever.query_expansions = load_query_expansions(CONFIG_PATH)
        retriever.context_sources = []
        retriever.storage = object()
        retriever.fixed_versions = {
            "luminosityfit": "a" * 40,
            "pandaroot": "b" * 40,
            "restgas_determination": "c" * 40,
        }
        retriever.vertex = SimpleNamespace(
            generate_json=MagicMock(side_effect=lambda prompt, schema, **kwargs: {
                "ranked_object_ids": [json.loads(prompt).get("untrusted_candidates", [{}])[0].get("object_id")]
            } if json.loads(prompt).get("untrusted_candidates") else {"ranked_object_ids": []})
        )
        # 30 dummy exact candidates
        dummy_exact = [
            {
                "object_id": f"ord_{i}",
                "source_id": "pandaroot",
                "source_version_id": f"pandaroot@{'b'*40}",
                "object_type": "source_file",
                "title": f"file_{i}",
                "text": f"text {i}",
                "locator": {"path": f"src/{i}.C"},
                "authority_level": "primary",
            }
            for i in range(30)
        ]
        retriever._exact = lambda *args: dummy_exact
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

    @pytest.mark.parametrize("overlap", [False, True])
    def test_req22_23_migrated_rule_reaches_structured_and_enters_k3(self, overlap):
        """Req 22-23: Migrated rule invokes structured replacement and enters rerank pool via K3."""
        retriever = self._setup_retriever_with_mocks()

        synth_candidate = {
            "object_id": "bridged_obj_1",
            "source_id": "restgas_determination",
            "source_version_id": f"restgas_determination@{'c'*40}",
            "object_type": "source_file",
            "title": "poca_handoff_impl",
            "text": "implementation of event_poca handoff",
            "locator": {"path": "src/event_poca.cxx"},
            "authority_level": "primary",
        }
        synth_receipt = {
            "bridge_status": "BRIDGED_CANDIDATE_INJECTED",
            "source_native_candidate_object_id": "bridged_obj_1",
            "evidence_provenance_origin_id": "origin_poca_1",
            "evidence_provenance_origin_type": "process",
            "source_id": "restgas_determination",
            "source_version_id": f"restgas_determination@{'c'*40}",
            "reachability_receipt_id": "reach_1",
            "locator": {"path": "src/event_poca.cxx"},
        }
        reach_receipt = {
            "reachability_receipt_id": "reach_1",
            "budget_consumed": 1,
        }
        mock_contrib = D3StructuredContribution(
            candidates=[],
            bridged_candidates=[synth_candidate],
            reachability_receipts=[reach_receipt],
            bridge_receipts=[synth_receipt],
            bridged_payloads={"bridged_obj_1": synth_candidate},
            resolution_receipt={"resolved_seeds": ["seed_1"]},
        )
        if overlap:
            # Ordinary channel text differs from canonical bridge materialization.
            synth_candidate["object_id"] = "ord_0"
            synth_receipt["source_native_candidate_object_id"] = "ord_0"
            mock_contrib.bridged_payloads = {"ord_0": synth_candidate}

        with patch(
            "panda_agent.retrieval.build_structured_contribution_from_storage",
            return_value=mock_contrib,
        ) as mock_builder:
            plan = retriever._preparse("Where is event_poca defined?")
            plan_obj = RetrievalPlan(
                intent="usage",
                target_repositories=["restgas_determination", "pandaroot"],
                resolved_versions=retriever.fixed_versions,
                concepts=plan.concepts,
                symbols=plan.symbols,
                concept_scopes={},
                source_budgets={"code": 1.0},
                required_source_types=["code"],
                analysis_diagnostics={
                    "matched_expansion_rules": list(plan.matched_expansion_rules),
                    "structured_replacement_rules": list(plan.structured_replacement_rules),
                },
            )
            retriever.analyze = MagicMock(return_value=plan_obj)
            result = retriever.retrieve("Where is event_poca defined?")
            retriever.analyze.assert_called_once_with("Where is event_poca defined?", d3_config=None)
            mock_builder.assert_called_once()
            assert retriever.vertex.generate_json.call_count == 1
            assert "structured_replacement" in result
            sr = result["structured_replacement"]
            assert sr["active_migrated_rule_ids"] == ["event_poca_handoff"]
            oid = "ord_0" if overlap else "bridged_obj_1"
            assert oid in sr["selected_candidate_ids"]
            assert sr["candidate_selectivity_receipts"][0]["text_presence"] > 0
            assert len(sr["final_rerank_pool_ids"]) == 30
            assert oid in sr["final_rerank_pool_ids"]
            if overlap:
                assert sr["reserved_ids"] == []
                assert sr["displaced_ordinary_ids"] == []
            else:
                assert oid in sr["reserved_ids"]
                assert "ord_29" in sr["displaced_ordinary_ids"]

    def test_req24_ordinary_non_migrated_retrieval_untouched(self):
        """Req 24: Ordinary non-migrated retrieval does not invoke structured replacement."""
        retriever = self._setup_retriever_with_mocks()
        with patch("panda_agent.retrieval.build_structured_contribution_from_storage") as mock_builder:
            plan = retriever._preparse("How to install software?")
            plan_obj = RetrievalPlan(
                intent="installation",
                target_repositories=["pandaroot"],
                resolved_versions=retriever.fixed_versions,
                concepts=[],
                symbols=[],
                concept_scopes={},
                source_budgets={"code": 1.0},
                required_source_types=[],
                analysis_diagnostics={
                    "matched_expansion_rules": list(plan.matched_expansion_rules),
                    "structured_replacement_rules": list(plan.structured_replacement_rules),
                },
            )
            result = retriever.retrieve("How to install software?", plan=plan_obj)
            mock_builder.assert_not_called()
            assert "structured_replacement" not in result

    def test_req25_reranker_call_count_remains_one(self):
        """Req 25: Reranker call count remains exactly one per retrieval."""
        retriever = self._setup_retriever_with_mocks()
        plan_obj = RetrievalPlan(
            intent="installation",
            target_repositories=["pandaroot"],
            resolved_versions=retriever.fixed_versions,
            concepts=[],
            symbols=[],
            concept_scopes={},
            source_budgets={"code": 1.0},
            required_source_types=[],
            analysis_diagnostics={"matched_expansion_rules": []},
        )
        retriever.retrieve("Install pandaroot", plan=plan_obj)
        assert retriever.vertex.generate_json.call_count == 1

    def test_req26_final_selector_preserves_policy(self):
        """Req 26: select_final_evidence remains unchanged."""
        retriever = self._setup_retriever_with_mocks()
        plan_obj = RetrievalPlan(
            intent="usage",
            target_repositories=["pandaroot"],
            resolved_versions=retriever.fixed_versions,
            concepts=[],
            symbols=[],
            concept_scopes={},
            source_budgets={"code": 1.0},
            required_source_types=["code"],
            analysis_diagnostics={"matched_expansion_rules": []},
        )
        result = retriever.retrieve("Usage question", plan=plan_obj)
        assert len(result["evidence"]) <= retriever.policies.final_evidence_limit


# ============================================================================
# 6. Anti-Shortcut Invariants (Req 27-29)
# ============================================================================

class TestAntiShortcutInvariants:
    """Requirements 27-29: Anti-shortcut enforcement."""

    def test_req27_no_query_rule_answer_mapping_in_production(self):
        """Req 27: No hard-coded query/rule -> object/path mapping exists in production code."""
        prod_files = [
            PROJECT_ROOT / "src" / "panda_agent" / "retrieval.py",
            PROJECT_ROOT / "src" / "panda_agent" / "d3_structured.py",
            PROJECT_ROOT / "src" / "panda_agent" / "config.py",
        ]
        forbidden_snippets = [
            "if rule_id == \"event_poca_handoff\":",
            "if rule.rule_id == \"event_poca_handoff\":",
            "if rule_id == \"restgas_profile_workflow\":",
            "if rule.rule_id == \"restgas_profile_workflow\":",
            "macro/target/ana_dpm.C",
            "macro/target/prod_aod_complete.C",
            "pgenerators/Target/PndTargetGenerator.cxx",
            "g036",
            "g021",
        ]
        for pfile in prod_files:
            content = pfile.read_text(encoding="utf-8")
            for snippet in forbidden_snippets:
                assert snippet not in content, f"Forbidden snippet '{snippet}' found in {pfile}"

    def test_req28_expected_benchmark_evidence_never_enters_runtime(self):
        """Req 28: Production runtime modules have no references to gold/expected evidence or benchmarks."""
        prod_files = [
            PROJECT_ROOT / "src" / "panda_agent" / "retrieval.py",
            PROJECT_ROOT / "src" / "panda_agent" / "d3_structured.py",
            PROJECT_ROOT / "src" / "panda_agent" / "config.py",
            PROJECT_ROOT / "src" / "panda_agent" / "entity_resolution.py",
        ]
        for py_file in prod_files:
            text = py_file.read_text(encoding="utf-8")
            assert "expected_evidence" not in text
            assert "gold_evidence" not in text
            assert "GoldEvidenceSelector" not in text

    def test_req29_no_evaluation_imports_in_production(self):
        """Req 29: Production code does not import from evaluation scripts or artifacts."""
        prod_dir = PROJECT_ROOT / "src" / "panda_agent"
        for py_file in prod_dir.rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert not alias.name.startswith("evaluation"), f"Production file {py_file} imports {alias.name}"
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        assert not node.module.startswith("evaluation"), f"Production file {py_file} imports from {node.module}"


# ============================================================================
# 7. Semantic Parity Against Frozen Evaluation Algorithms (Section 19)
# ============================================================================

class TestEvaluationParity:
    """Verifies that production selectivity and admission match frozen evaluation algorithms."""

    @pytest.mark.parametrize("scope,symbols", [
        (["pandaroot", "restgas_determination"], ["PndTrack"]),
        (["pandaroot"], ["PndTrack"]),
        (["pandaroot", "restgas_determination"], []),
        (["unrelated_repo"], ["PndTrack"]),
    ])
    def test_selectivity_v2_parity(self, scope, symbols):
        """Semantic parity test against evaluation.scripts.d3_5_a5_r2_selectivity."""
        import scripts.d3_5_a5_r2_selectivity as eval_sel

        plan = {
            "target_repositories": scope,
            "symbols": symbols,
            "concepts": ["track_reconstruction"],
        }
        candidates = [
            {
                "candidate_object_id": f"cand_{i}",
                "source_id": "pandaroot" if i % 2 == 0 else "restgas_determination",
                "source_version_id": "v1",
                "object_type": "source_file",
                "provenance_origin_ids": [f"orig_{i % 3}", "shared_origin"],
                "locator_path": f"src/pnd_track_{i}.C",
                "min_structural_distance_transitions": i,
            }
            for i in range(12)
        ]
        registry = {
            f"cand_{i}": {
                "object_id": f"cand_{i}",
                "title": f"PndTrack header {i}",
                "source_id": "pandaroot" if i % 2 == 0 else "restgas_determination",
                "text_payload_2000": f"PndTrack tracking reconstruction details {i}",
                "object_type": "source_file",
                "locator": {"path": f"src/pnd_track_{i}.C"},
            }
            for i in range(12)
        }
        question = "Where is PndTrack tracking reconstruction implemented?"

        # Production run
        channels = {"dense": ["cand_7", "cand_3"], "exact": ["cand_3"]}
        prod_res = select_structured_candidates_v2(question, plan, candidates, registry, channels)

        # Eval run
        eval_case = {
            "case_id": "synthetic_parity_case",
            "frozen_plan_fields": plan,
            "question": {"query": question},
            "arms": {"STRUCTURED_BRIDGED": {"channel_rankings": channels}},
            "unbridged_graph_ordering": [],
            "eligible_governed_bridge_candidates": candidates,
        }
        eval_res = eval_sel.select_v2(eval_case, registry)

        assert prod_res["selected_object_ids"] == eval_res["selected_object_ids"]
        assert prod_res["selected_bridge_candidate_count"] == eval_res["selected_bridge_candidate_count"]
        assert prod_res["selected_rank_keys"] == eval_res["selected_rank_keys"]
        assert prod_res["candidate_receipts"] == [
            {key: value for key, value in row.items() if key != "a2_disposition"}
            for row in eval_res["candidate_receipts"]
        ]

    def test_admission_k3_parity(self):
        """Semantic parity test against evaluation.scripts.d3_5_a6_phase1_admission."""
        import scripts.d3_5_a6_phase1_admission as eval_adm

        baseline = [f"base_{i}" for i in range(30)]
        v2_order = ["base_1", "synth_new_1", "synth_new_2", "base_5", "synth_new_3", "synth_new_4"]

        # Reservable parity
        prod_reservable = reservable_bridge(v2_order, baseline)
        eval_reservable = eval_adm.reservable_bridge(v2_order, baseline)
        assert prod_reservable == eval_reservable

        # Treatment pool parity
        prod_pool = build_treatment_pool(baseline, prod_reservable, k=3)
        eval_pool = eval_adm.build_treatment_pool(baseline, eval_reservable, k=3)

        assert prod_pool["treatment_pool_object_ids"] == eval_pool["treatment_pool_object_ids"]
        assert prod_pool["reserved_bridge_candidate_ids"] == eval_pool["reserved_bridge_candidate_ids"]
        assert prod_pool["displaced_object_ids"] == eval_pool["displaced_object_ids"]
        assert prod_pool["pool_size"] == eval_pool["pool_size"]
