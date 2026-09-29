"""Synthetic controls for bounded G4 R2 rerank opportunity."""

import json
from types import SimpleNamespace

from panda_agent.models import RetrievalPlan
from panda_agent.qa import QAAgent
from panda_agent.retrieval import Retriever


class EchoReranker:
    def __init__(self) -> None:
        self.offered_ids: list[str] = []

    def generate_json(self, prompt, schema, *, system_instruction):
        request = json.loads(prompt)
        self.offered_ids = [item["object_id"] for item in request["untrusted_candidates"]]
        return {"ranked_object_ids": self.offered_ids}


class PoolOnlyRetriever(Retriever):
    def __init__(self, vertex: EchoReranker) -> None:
        self.vertex = vertex
        self.policies = SimpleNamespace(final_evidence_limit=12)
        self.context_sources = ["fictional_paper"]

    def _source_type(self, payload):
        return payload.get("source_type", "code")

    def _prioritize_and_select_evidence(self, **kwargs):
        return kwargs["ordered"], kwargs["ordered"][:30], [], [], [], []


def candidate(oid: str, **changes) -> dict:
    item = {
        "object_id": oid,
        "source_id": "fictional_repo",
        "source_version_id": "fictional_repo@rev-a",
        "object_type": "code_chunk",
        "title": oid,
        "text": f"Synthetic evidence for {oid}.",
        "locator": {"path": f"src/{oid}.py"},
    }
    item.update(changes)
    return item


def plan_for(**budgets) -> RetrievalPlan:
    return RetrievalPlan(
        intent="api",
        target_repositories=["fictional_repo"],
        resolved_versions={"fictional_repo": "rev-a"},
        source_budgets=budgets,
    )


def consensus_snapshots(extra=None):
    rows = [candidate(f"synthetic_consensus_{i:02d}") for i in range(30)]
    snapshots = [
        {"pass_origin": "initial", "rankings": {"exact": rows[:15], "sparse": rows[:15]}},
        {"pass_origin": "targeted", "rankings": {"exact": rows[15:], "sparse": rows[15:]}},
    ]
    if extra:
        snapshots[0]["rankings"].update(extra)
    return snapshots


def run_pool(plan, snapshots):
    reranker = EchoReranker()
    result = PoolOnlyRetriever(reranker).consolidate_and_select_candidates(
        "Synthetic question", plan, snapshots
    )
    return result, reranker.offered_ids


def reasons(result):
    return {entry["object_id"]: entry["reason"] for entry in result["rerank_pool_entries"]}


class NormalPoolRetriever(PoolOnlyRetriever):
    def __init__(self, rankings, channel_origins=None):
        super().__init__(EchoReranker())
        self.policies.candidate_pool_per_channel = 20
        self.rankings = {channel: [] for channel in ("exact", "dense", "sparse", "workflow", "graph")}
        self.rankings.update(rankings)
        self.channel_origins = channel_origins or {}

    def _collect_channel_rankings(self, question, plan, limit):
        self._specialized_origins = self.channel_origins
        semantic_query = SimpleNamespace(
            text=question, intent=plan.intent, symbols=[],
            as_dict=lambda: {"text": question, "intent": plan.intent, "symbols": []},
        )
        return self.rankings, semantic_query, []

    def _apply_structured_replacement(self, question, plan, rankings, pool, payloads):
        return pool, [], None


def normal_consensus_rankings(necessary):
    rows = [candidate(f"synthetic_consensus_{i:02d}") for i in range(30)]
    return {
        "exact": rows[:20], "sparse": rows[:20], "dense": [necessary],
        "workflow": rows[20:], "graph": rows[20:],
    }


def test_r2_normal_retrieve_uses_policy_role_frontier():
    necessary = candidate("synthetic_normal_necessary")
    retriever = NormalPoolRetriever(
        normal_consensus_rankings(necessary),
        {"workflow": ["normal"] * 10, "graph": ["normal"] * 10},
    )
    result = retriever.retrieve("Synthetic question", plan=plan_for(code=1.0))

    assert necessary["object_id"] not in result["fusion_scores"]
    assert necessary["object_id"] in retriever.vertex.offered_ids
    assert reasons(result)[necessary["object_id"]] == "policy_role_frontier"


def test_normal_supplements_and_frontier_share_global_membership_and_truthful_receipt():
    necessary = candidate("synthetic_normal_necessary")
    rankings = normal_consensus_rankings(necessary)
    origins = {"workflow": ["normal"] * 10, "graph": ["normal"] * 10}
    external = candidate("synthetic_external_supplement")
    supplements = [external, rankings["exact"][0]]

    class SupplementRetriever(NormalPoolRetriever):
        def _apply_structured_replacement(self, question, plan, rankings, pool, payloads):
            self.discovery_pool = list(pool)
            payloads[external["object_id"]] = external
            eligible = [item["object_id"] for item in supplements]
            treatment = [*pool[:-1], external["object_id"]]
            return treatment, eligible, {
                "reserved_ids": [external["object_id"]],
                "eligible_supplemental_ids": eligible,
                "displaced_ordinary_ids": [pool[-1]],
                "final_rerank_pool_ids": treatment,
            }

    plan = plan_for(code=1.0)
    retriever = SupplementRetriever(rankings, origins)
    result = retriever.retrieve("Synthetic question", plan=plan)
    offered = retriever.vertex.offered_ids
    receipt = result["structured_replacement"]
    counts = list(reasons(result).values())
    assert retriever.discovery_pool == list(result["fusion_scores"])
    assert necessary["object_id"] not in retriever.discovery_pool
    assert len(offered) == len(set(offered)) == 30
    assert counts.count("ordinary_rrf") > counts.count("policy_role_frontier")
    assert offered[-2:] == [item["object_id"] for item in supplements]
    assert all(reasons(result)[item["object_id"]] == "structured_supplemental" for item in supplements)
    assert reasons(result)[necessary["object_id"]] == "policy_role_frontier"
    assert receipt["final_rerank_pool_ids"] == offered
    assert receipt["reserved_ids"] == [external["object_id"]]
    assert receipt["displaced_ordinary_ids"] == [retriever.discovery_pool[-1]]

    global_result, global_offered = run_pool(plan, [{
        "rankings": retriever.rankings, "channel_origins": origins,
        "supplemental_candidates": supplements,
    }])
    assert offered == global_offered
    assert result["rerank_pool_entries"] == global_result["rerank_pool_entries"]


def test_normal_pool_without_omitted_challenger_preserves_ordinary_rrf():
    rows = [candidate(f"synthetic_ordinary_{i:02d}") for i in range(8)]
    retriever = NormalPoolRetriever({"exact": rows, "dense": list(reversed(rows[:4]))})
    result = retriever.retrieve("Synthetic question", plan=plan_for(code=1.0))
    assert retriever.vertex.offered_ids == list(result["fusion_scores"])
    assert set(reasons(result).values()) == {"ordinary_rrf"}


def test_normal_specialized_fallback_and_missing_origin_do_not_gain_frontier():
    workflow = candidate("synthetic_normal_workflow_fallback")
    graph = candidate("synthetic_normal_graph_fallback")
    rankings = normal_consensus_rankings(candidate("unused"))
    rankings["dense"] = []
    rankings["workflow"] = [*rankings["workflow"], workflow]
    rankings["graph"] = [*rankings["graph"], graph]
    for origins in ({
        "workflow": ["normal"] * 10 + ["generic_fallback"],
        "graph": ["normal"] * 10 + ["generic_fallback"],
    }, {}):
        retriever = NormalPoolRetriever(rankings, origins)
        result = retriever.retrieve("Synthetic question", plan=plan_for(code=0.5, workflow=0.25, graph=0.25))
        assert workflow["object_id"] not in reasons(result)
        assert graph["object_id"] not in reasons(result)


def test_normal_qa_detailed_diagnostics_preserve_actual_pool_receipt():
    necessary = candidate("synthetic_normal_necessary")
    retriever = NormalPoolRetriever(
        normal_consensus_rankings(necessary),
        {"workflow": ["normal"] * 10, "graph": ["normal"] * 10},
    )
    retriever.analyze = lambda question, **kwargs: plan_for(code=1.0)
    agent = QAAgent.__new__(QAAgent)
    agent.retriever = retriever
    agent.decompose_question = lambda question, **kwargs: {"points": [{
        "answer_point_id": "synthetic.point", "text": "Synthetic aspect",
        "support_spans": [question], "required_relations": [],
    }]}
    agent._stats_snapshot = lambda: {}
    agent._model_usage_delta = lambda before: {}
    agent._model_roles_diagnostics = lambda: {}
    agent.graph = SimpleNamespace(invoke=lambda initial: {
        **agent._retrieve(initial),
        "result": {"status": "insufficient_evidence", "answer": "Synthetic no-answer result"},
        "answer_point_audit": {},
    })
    detailed = agent.run_detailed("Synthetic question")
    entries = detailed["diagnostics"]["rerank_pool_entries"]
    assert [entry["object_id"] for entry in entries] == retriever.vertex.offered_ids
    assert {entry["object_id"]: entry["reason"] for entry in entries}[necessary["object_id"]] == "policy_role_frontier"
    assert "rerank_pool_entries" not in detailed["result"]


def test_r2_a_valid_single_channel_policy_candidate_gets_rerank_opportunity():
    plan = RetrievalPlan(
        intent="api",
        target_repositories=["fictional_repo"],
        resolved_versions={"fictional_repo": "rev-a"},
        source_budgets={"code": 1.0},
    )
    consensus = [candidate(f"synthetic_consensus_{i:02d}") for i in range(30)]
    necessary = candidate("synthetic_necessary")
    snapshots = [
        {"pass_origin": "initial", "rankings": {
            "exact": consensus[:15],
            "sparse": consensus[:15],
            "dense": [necessary],
        }},
        {"pass_origin": "targeted", "rankings": {
            "exact": consensus[15:],
            "sparse": consensus[15:],
        }},
    ]
    reranker = EchoReranker()
    result = PoolOnlyRetriever(reranker).consolidate_and_select_candidates(
        "What is the synthetic necessary evidence?", plan, snapshots
    )

    assert result["status"] == "success"
    assert result["best_channel_ranks"][necessary["object_id"]] == {"dense": 1}
    assert necessary["object_id"] in result["fused_candidate_ids"]
    assert necessary["object_id"] in reranker.offered_ids
    assert reasons(result)[necessary["object_id"]] == "policy_role_frontier"


def test_r2_b_weak_single_role_noise_stays_outside_capacity():
    challengers = [candidate(f"synthetic_challenger_{i:02d}") for i in range(15)]
    snapshots = consensus_snapshots({"dense": challengers})
    result, offered = run_pool(plan_for(code=1.0), snapshots)
    assert result["status"] == "success"
    assert all(item["object_id"] in offered for item in challengers[:12])
    assert challengers[-1]["object_id"] not in offered
    assert sum(reason == "policy_role_frontier" for reason in reasons(result).values()) == 12


def test_r2_c_rrf_backbone_remains_strict_majority_across_roles():
    challengers = [
        candidate(f"synthetic_role_{role}_{i}", source_type=role)
        for role in ("code", "paper", "documentation") for i in range(6)
    ]
    snapshots = consensus_snapshots({"dense": challengers})
    result, offered = run_pool(plan_for(code=0.34, paper=0.33, documentation=0.33), snapshots)
    counts = list(reasons(result).values())
    assert counts.count("ordinary_rrf") > counts.count("policy_role_frontier")
    assert counts.count("ordinary_rrf") == 17
    assert counts.count("policy_role_frontier") == 13
    assert "synthetic_consensus_00" in offered


def test_r2_d_global_bound_with_supplements_and_many_challengers():
    snapshots = consensus_snapshots({"dense": [candidate(f"synthetic_extra_{i:02d}") for i in range(20)]})
    snapshots[0]["supplemental_candidates"] = [candidate(f"synthetic_supp_{i:02d}") for i in range(30)]
    result, offered = run_pool(plan_for(code=1.0), snapshots)
    assert len(offered) == len(set(offered)) == 30
    assert all(reason == "structured_supplemental" for reason in reasons(result).values())


def test_r2_e_deduplicates_channels_passes_roles_and_supplement_overlap():
    shared = candidate("synthetic_shared", source_type="workflow")
    snapshots = consensus_snapshots({"dense": [shared], "workflow": [shared]})
    snapshots[0]["channel_origins"] = {"workflow": ["normal"]}
    snapshots[1]["rankings"]["dense"] = [shared]
    snapshots[1]["supplemental_candidates"] = [shared]
    result, offered = run_pool(plan_for(code=0.5, workflow=0.5), snapshots)
    assert offered.count(shared["object_id"]) == 1
    assert reasons(result)[shared["object_id"]] == "structured_supplemental"
    assert result["best_channel_ranks"][shared["object_id"]] == {"dense": 1, "workflow": 1}
    assert len(result["pass_occurrences"][shared["object_id"]]) == 4
    assert result["pass_occurrences"][shared["object_id"]][1]["origin"] == "normal"


def test_r2_f_invalid_candidates_and_inconsistent_payloads_have_no_frontier():
    invalid = [
        candidate("synthetic_wrong_repo", source_id="other_repo"),
        candidate("synthetic_wrong_version", source_version_id="fictional_repo@rev-b"),
        candidate("synthetic_unusable", text=""),
    ]
    snapshots = consensus_snapshots({"dense": invalid})
    result, _ = run_pool(plan_for(code=1.0), snapshots)
    assert not any(oid in reasons(result) for oid in [item["object_id"] for item in invalid])
    snapshots[1]["rankings"]["dense"] = [candidate("synthetic_wrong_repo", title="conflict")]
    conflict, _ = run_pool(plan_for(code=1.0), snapshots)
    assert conflict["status"] == "consistency_failure"


def test_r2_f_same_specialized_object_requires_normal_origin():
    for role in ("workflow", "graph"):
        item = candidate(f"synthetic_{role}_origin_pair")
        plan = plan_for(code=0.5, **{role: 0.5})
        for origin, expected in (("normal", True), ("generic_fallback", False)):
            snapshots = consensus_snapshots({role: [item]})
            snapshots[0]["channel_origins"] = {role: [origin]}
            result, _ = run_pool(plan, snapshots)
            assert (reasons(result).get(item["object_id"]) == "policy_role_frontier") is expected


def test_r2_g_supplement_reservation_reduces_frontier_to_zero():
    challenger = candidate("synthetic_challenger")
    snapshots = consensus_snapshots({"dense": [challenger]})
    supp = [candidate(f"synthetic_supp_{i:02d}") for i in range(28)]
    snapshots[0]["supplemental_candidates"] = supp
    result, offered = run_pool(plan_for(code=1.0), snapshots)
    assert len(offered) == 30
    assert offered[-28:] == [item["object_id"] for item in supp]
    assert challenger["object_id"] not in offered
    assert list(reasons(result).values()).count("policy_role_frontier") == 0


def test_r2_h_ties_and_repeated_passes_are_deterministic():
    a = candidate("synthetic_a", source_type="paper")
    b = candidate("synthetic_b", source_type="documentation")
    snapshots = consensus_snapshots({"dense": [a, b]})
    snapshots[1]["rankings"]["dense"] = [a, b]
    plan = plan_for(code=0.5, paper=0.25, documentation=0.25)
    first, first_offered = run_pool(plan, snapshots)
    second, second_offered = run_pool(plan, snapshots)
    assert first_offered == second_offered
    assert first["rerank_pool_entries"] == second["rerank_pool_entries"]
    assert reasons(first)[a["object_id"]] == "policy_role_frontier"
    assert reasons(first)[b["object_id"]] == "policy_role_frontier"


def test_r2_i_paper_and_normal_specialized_roles_without_fallback_preference():
    paper = candidate("synthetic_paper", source_id="fictional_paper", source_version_id="fictional_paper@rev-a", source_type="paper")
    workflow = candidate("synthetic_workflow")
    graph = candidate("synthetic_graph")
    workflow_fallback = candidate("synthetic_workflow_fallback")
    graph_fallback = candidate("synthetic_graph_fallback")
    snapshots = consensus_snapshots({
        "dense": [paper],
        "workflow": [workflow, workflow_fallback],
        "graph": [graph, graph_fallback],
    })
    snapshots[0]["channel_origins"] = {
        "workflow": ["normal", "generic_fallback"],
        "graph": ["normal", "generic_fallback"],
    }
    plan = plan_for(code=0.25, paper=0.25, workflow=0.25, graph=0.25)
    result, offered = run_pool(plan, snapshots)
    for item in (paper, workflow, graph):
        assert item["object_id"] in offered
        assert reasons(result)[item["object_id"]] == "policy_role_frontier"
    for item in (workflow_fallback, graph_fallback):
        assert item["object_id"] not in offered
    del snapshots[0]["channel_origins"]
    historical, _ = run_pool(plan, snapshots)
    assert workflow["object_id"] not in reasons(historical)
    assert graph["object_id"] not in reasons(historical)


def test_specialized_query_branches_record_origin_at_the_source():
    class Connection:
        def __init__(self, batches):
            self.batches = iter(batches)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, *args):
            return SimpleNamespace(fetchall=lambda: next(self.batches))

    def retriever_with_rows(*batches):
        retriever = Retriever.__new__(Retriever)
        connection = Connection(batches)
        retriever.storage = SimpleNamespace(connect=lambda: connection)
        retriever.policies = SimpleNamespace(max_relation_hops=2)
        retriever.context_sources = []
        retriever._specialized_origins = {}
        retriever._row = lambda row: row
        return retriever

    workflow_plan = plan_for(code=0.5, workflow=0.5).model_copy(update={"required_source_types": ["workflow"]})
    workflow_item = candidate("synthetic_workflow", object_type="workflow")
    normal = retriever_with_rows([workflow_item])
    assert normal._workflow("synthetic question", workflow_plan, 20) == [workflow_item]
    assert normal._specialized_origins["workflow"] == ["normal"]
    fallback = retriever_with_rows([], [workflow_item])
    assert fallback._workflow("synthetic question", workflow_plan, 20) == [workflow_item]
    assert fallback._specialized_origins["workflow"] == ["generic_fallback"]

    graph_plan = plan_for(code=0.5, graph=0.5).model_copy(update={"required_source_types": ["graph"]})
    graph_item = candidate("synthetic_graph")
    normal = retriever_with_rows([graph_item])
    assert normal._graph([graph_item], graph_plan, 20) == [graph_item]
    assert normal._specialized_origins["graph"] == ["normal"]
    fallback = retriever_with_rows([], [graph_item])
    assert fallback._graph([graph_item], graph_plan, 20) == [graph_item]
    assert fallback._specialized_origins["graph"] == ["generic_fallback"]


def test_e3_targeted_snapshot_forwards_specialized_origin_sidecar():
    class CapturingRetriever:
        policies = SimpleNamespace(final_evidence_limit=12)

        def collect_channel_candidates(self, question, plan):
            return {
                "rankings": {"graph": [candidate("synthetic_targeted_graph")]},
                "channel_origins": {"graph": ["normal"]},
                "supplemental_candidates": [],
            }

        def consolidate_and_select_candidates(self, **kwargs):
            self.snapshots = kwargs["pass_snapshots"]
            return {"status": "no_gain", "selected_evidence": [], "payloads": {}}

    agent = QAAgent.__new__(QAAgent)
    agent.retriever = CapturingRetriever()
    plan = plan_for(code=0.5, graph=0.5)
    state = {
        "question": "Synthetic question",
        "original_plan": plan.model_dump(mode="json"),
        "bundle": {"evidence": []},
        "candidate_snapshots": [{"pass_origin": "initial", "rankings": {"exact": []}}],
        "missing_answer_point_ids": ["synthetic.point"],
        "runtime_answer_points": [{"answer_point_id": "synthetic.point", "text": "Synthetic aspect"}],
    }
    result = agent._missing_point_retrieve(state)
    assert result["e3_trace"]["atomic_update_status"] == "no_gain"
    assert agent.retriever.snapshots[-1]["channel_origins"] == {"graph": ["normal"]}
