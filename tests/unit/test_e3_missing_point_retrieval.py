"""Focused deterministic unit tests for E3-A1 Missing-Point Targeted Retrieval.

Strictly adheres to evaluation/E3_A0_MISSING_POINT_TARGETED_RETRIEVAL_CONTRACT.md:
- Fake/mock only, zero real external/network calls, zero real scientific model calls.
- Verifies T1-T20 and Sentinels 1-3.
"""

from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from panda_agent.models import ClaimCitation, QAResult, QAStatus, RetrievalPlan, SourceLocator, stable_id
from panda_agent.qa import (
    DEFAULT_ANSWER_POINT_MODE,
    QAAgent,
    _build_missing_point_retrieval_objective,
    _claim_matches_retained,
)
from panda_agent.retrieval import Retriever
from test_qa import CatalogStorage, bundle_for, code_evidence


QUESTION = "What is the PndPidCorrelator configuration and how are tracks filtered?"
POINTS = [
    {"answer_point_id": "point.1", "text": "PndPidCorrelator configuration options."},
    {"answer_point_id": "point.2", "text": "Track filtering implementation in fillData."},
]


def make_evidence(
    object_id: str,
    path: str | None = None,
    text: str = "void PndPidCorrelator::fillData() { successfullyPassedFilters(); }",
    source_id: str = "pandaroot",
    source_version_id: str = "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
    channel: str = "exact",
    score: float = 1.0,
    start_line: int | None = None,
) -> dict[str, Any]:
    default_path = f"src/{object_id}.cxx" if path is None else path
    s_line = start_line if start_line is not None else 10
    eid = stable_id(object_id, channel, prefix="evidence")
    return {
        "evidence_id": eid,
        "object_id": object_id,
        "source_id": source_id,
        "source_version_id": source_version_id,
        "text": text,
        "locator": {
            "path": default_path,
            "start_line": s_line,
            "end_line": s_line + 15,
            "symbol": f"PndPidCorrelator::{object_id}",
        },
        "retrieval_channels": [channel],
        "score": score,
        "authority_level": "primary",
    }


def make_claim(
    cid: str = "c1",
    point: str = "point.1",
    text: str = "The PndPidCorrelator configures track filters.",
    evidence_ids: list[str] | None = None,
) -> dict[str, Any]:
    default_eid = stable_id("obj1", "exact", prefix="evidence")
    return {
        "claim_id": cid,
        "claim_text": text,
        "evidence_ids": evidence_ids or [default_eid],
        "answer_point_ids": [point],
        "declared_answer_point_ids": [point],
    }


def make_review(
    supported: bool = True,
    mappings: dict[str, list[str]] | None = None,
    missing: list[str] | None = None,
    unsupported: list[str] | None = None,
    irrelevant: list[str] | None = None,
    requirements: list[str] | None = None,
    reason: str = "",
) -> dict[str, Any]:
    return {
        "supported": supported,
        "unsupported_claim_ids": list(unsupported or []),
        "irrelevant_claim_ids": list(irrelevant or []),
        "missing_requirement_ids": list(requirements or []),
        "reason": reason,
        "claim_answer_point_mappings": [
            {"claim_id": k, "answer_point_ids": v} for k, v in (mappings or {}).items()
        ],
        "missing_answer_point_ids": list(missing or []),
    }


def make_proposal(
    points_text: list[str] | None = None,
    support_spans: list[list[str]] | None = None,
) -> dict[str, Any]:
    texts = points_text or [
        "PndPidCorrelator configuration options.",
        "Track filtering implementation in fillData.",
    ]
    spans = support_spans or [
        ["PndPidCorrelator", "configuration"],
        ["tracks", "filtered"],
    ]
    return {
        "points": [
            {
                "text": t,
                "support_spans": spans[i],
                "facet_type": "definition",
            }
            for i, t in enumerate(texts)
        ],
        "ambiguity": {"status": "clear", "reason": ""},
    }


class FakeVertex:
    def __init__(
        self,
        answers: list[dict[str, Any]] | None = None,
        reviews: list[dict[str, Any]] | None = None,
        revisions: list[dict[str, Any]] | None = None,
        decomposition: dict[str, Any] | None = None,
        rerank_order: list[str] | None = None,
    ) -> None:
        eid1 = stable_id("obj1", "exact", prefix="evidence")
        eid2 = stable_id("obj2", "exact", prefix="evidence")
        self.answers = answers or [make_claim("c1", "point.1", "PndPidCorrelator configuration.", [eid1])]
        self.reviews = list(reviews or [make_review(mappings={"c1": ["point.1"]}, missing=["point.2"])])
        self.revisions = revisions or [make_claim("c2", "point.2", "Track filtering in fillData via successfullyPassedFilters.", [eid2])]
        self.decomposition = decomposition or make_proposal()
        self.rerank_order = rerank_order
        self.calls: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []

    def stats_snapshot(self) -> dict[str, int]:
        return {
            "model_calls": len(self.calls),
            "generation_calls": len(self.calls),
            "token_usage": len(self.calls) * 10,
            "embedding_calls": 0,
        }

    def stats_delta(self, before: dict[str, int]) -> dict[str, int]:
        return {k: v - before.get(k, 0) for k, v in self.stats_snapshot().items()}

    def generate_json(self, prompt: str, schema: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        p = json.loads(prompt)
        self.calls.append((p, deepcopy(schema), kwargs))
        task = p.get("task")
        if task == "decompose_user_question":
            if isinstance(self.decomposition, Exception):
                raise self.decomposition
            return deepcopy(self.decomposition)
        if task == "review_claim_support_and_relevance":
            if not self.reviews:
                return make_review()
            return deepcopy(self.reviews.pop(0))
        if task == "revise_unsupported_claims_once":
            return {"claims": deepcopy(self.revisions)}
        if task == "rerank_evidence":
            cands = [c["object_id"] for c in p.get("untrusted_candidates", [])]
            if self.rerank_order:
                ordered = [x for x in self.rerank_order if x in cands]
                remaining = [x for x in cands if x not in ordered]
                return {"ranked_object_ids": [*ordered, *remaining]}
            return {"ranked_object_ids": cands}
        return {"claims": deepcopy(self.answers)}


class FakeE3Retriever:
    def __init__(
        self,
        initial_bundle: dict[str, Any],
        targeted_candidates: dict[str, list[dict[str, Any]]] | None = None,
        policies: Any = None,
        vertex: Any = None,
    ) -> None:
        self.bundle = initial_bundle
        self.storage = CatalogStorage([])
        self.targeted_candidates = targeted_candidates or {}
        self.policies = policies
        self.vertex = vertex
        self.retrieve_calls: list[tuple[str, Any, bool]] = []
        self.collect_calls: list[tuple[str, Any]] = []
        self.consolidate_calls: list[dict[str, Any]] = []
        self.agent: Any = None

    def retrieve(
        self,
        question: str,
        plan: Any = None,
        capture_candidates: bool = False,
    ) -> dict[str, Any]:
        self.retrieve_calls.append((question, plan, capture_candidates))
        bundle = deepcopy(self.bundle)
        if not capture_candidates:
            bundle.pop("candidate_snapshot", None)
        elif "candidate_snapshot" not in bundle:
            bundle["candidate_snapshot"] = {
                "pass_origin": "initial",
                "rankings": {
                    "exact": [deepcopy(item) for item in bundle.get("evidence", [])]
                },
            }
        return bundle

    def collect_channel_candidates(self, question: str, plan: Any = None) -> dict[str, list[dict[str, Any]]]:
        self.collect_calls.append((question, plan))
        return deepcopy(self.targeted_candidates)

    def consolidate_and_select_candidates(
        self,
        original_question: str,
        plan: RetrievalPlan,
        pass_snapshots: list[dict[str, Any]],
        current_selected_evidence: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        self.consolidate_calls.append({
            "original_question": original_question,
            "plan": plan,
            "pass_snapshots": pass_snapshots,
            "current_selected_evidence": current_selected_evidence,
        })
        dummy_retriever = DummyRetriever(vertex=self.vertex, policies=self.policies)
        return Retriever.consolidate_and_select_candidates(
            dummy_retriever,
            original_question=original_question,
            plan=plan,
            pass_snapshots=pass_snapshots,
            current_selected_evidence=current_selected_evidence,
        )


class DummyRetriever(Retriever):
    def __init__(self, vertex: Any = None, policies: Any = None) -> None:
        self.vertex = vertex
        self.policies = policies

    def _source_type(self, payload: Any) -> str:
        return getattr(payload, "get", lambda k, d=None: d)("source_type") or "code"


def make_plan(**kwargs: Any) -> RetrievalPlan:
    base = bundle_for([])["plan"]
    base["source_budgets"] = {"code": 1.0}
    base.update(kwargs)
    return RetrievalPlan.model_validate(base)


def make_agent(
    tmp_path: Path,
    vertex: FakeVertex | None = None,
    retriever: FakeE3Retriever | None = None,
    ev1: dict[str, Any] | None = None,
    ev2: dict[str, Any] | None = None,
) -> QAAgent:
    e1 = ev1 or make_evidence("obj1", path="src/PndPidCorrelator1.cxx", text="void PndPidCorrelator::Init() {}")
    e2 = ev2 or make_evidence("obj2", path="src/PndPidCorrelator2.cxx", text="void PndPidCorrelator::fillData() { successfullyPassedFilters(); }")
    b = bundle_for([e1])
    b["plan"]["source_budgets"] = {"code": 1.0}
    v = vertex or FakeVertex()
    r = retriever or FakeE3Retriever(
        initial_bundle=b,
        targeted_candidates={"exact": [deepcopy(e2)]},
        vertex=v,
    )
    if r.vertex is None:
        r.vertex = v
    agent = QAAgent(tmp_path, retriever=r, vertex=v)
    r.agent = agent
    return agent


# ---------------------------------------------------------------------------
# Test Suite: T1 - T20 & Sentinels 1 - 3
# ---------------------------------------------------------------------------

def test_t1_legacy_mode_never_triggers_e3(tmp_path: Path) -> None:
    """T1: Normal QA mode (legacy_question_core) never triggers E3."""
    a = make_agent(tmp_path)
    out = a.run_detailed(QUESTION)
    assert a.retriever.collect_calls == []
    assert out["diagnostics"]["targeted_retrieval_count"] == 0
    assert "e3_trace" not in out["diagnostics"]


def test_t2_shadow_mode_never_triggers_e3(tmp_path: Path) -> None:
    """T2: Diagnostic shadow mode (shadow_e1_v2) never triggers E3."""
    v = FakeVertex(
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
        ],
        revisions=[],
    )
    a = make_agent(tmp_path, vertex=v)
    out = a.run_answer_point_coverage_diagnostic(QUESTION)
    assert a.retriever.collect_calls == []
    audit = out["diagnostics"]["answer_point_audit"]
    assert audit["missing_answer_point_ids"] == ["point.2"]
    assert "e3_trace" not in out["diagnostics"]


def test_t3_runtime_complete_coverage_skips_e3(tmp_path: Path) -> None:
    """T3: runtime_e1_v2 with complete first-pass coverage skips E3."""
    e1 = make_evidence("obj1", path="src/PndPidCorrelator1.cxx", text="void PndPidCorrelator::Init() {}")
    e2 = make_evidence("obj2", path="src/PndPidCorrelator2.cxx", text="void PndPidCorrelator::fillData() { successfullyPassedFilters(); }")
    b = bundle_for([e1, e2])
    b["plan"]["source_budgets"] = {"code": 1.0}
    b["candidate_snapshot"] = {
        "pass_origin": "initial",
        "rankings": {"exact": [deepcopy(e1), deepcopy(e2)]},
    }
    v = FakeVertex(
        answers=[
            make_claim("c1", "point.1", "PndPidCorrelator configuration.", [e1["evidence_id"]]),
            make_claim("c2", "point.2", "Track filtering in fillData via successfullyPassedFilters.", [e2["evidence_id"]]),
        ],
        reviews=[make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[])],
    )
    r = FakeE3Retriever(initial_bundle=b, vertex=v)
    a = make_agent(tmp_path, vertex=v, retriever=r)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert a.retriever.collect_calls == []
    trace = out["diagnostics"]["e3_trace"]
    assert trace["triggered"] is False
    assert trace["trigger_reason"] == "no_missing_answer_points"


def test_t4_runtime_genuine_missing_point_triggers_exactly_one_e3(tmp_path: Path) -> None:
    """T4: Genuine missing point triggers exactly one E3 retrieval pass and revision."""
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    eid2 = stable_id("obj2", "exact", prefix="evidence")
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.", [eid1])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),  # First review
            make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[]),  # Second review
        ],
        revisions=[make_claim("c2", "point.2", "Track filtering in fillData via successfullyPassedFilters.", [eid2])],
    )
    a = make_agent(tmp_path, vertex=v)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert len(a.retriever.collect_calls) == 1
    trace = out["diagnostics"]["e3_trace"]
    assert trace["triggered"] is True
    assert trace["missing_point_retrieval_count"] == 1
    assert trace["post_retrieval_missing_point_result"] == "complete"
    assert trace["recovered_on_revision"] is True
    assert trace["recovered_answer_point_ids"] == ["point.2"]


def test_t5_collection_query_exact_missing_point_text_order(tmp_path: Path) -> None:
    """T5: Retrieval query contains original question + exact missing point text in point order."""
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.")],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[]),
        ],
    )
    a = make_agent(tmp_path, vertex=v)
    a._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert len(a.retriever.collect_calls) == 1
    query, _ = a.retriever.collect_calls[0]
    expected_text = POINTS[1]["text"]
    assert QUESTION in query
    assert f"- {expected_text}" in query
    assert "Target missing question aspects:" in query


def test_t6_collection_query_excludes_forbidden_inputs(tmp_path: Path) -> None:
    """T6: Collection query excludes Gold, missing requirements, review reasons, draft claims."""
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    eid2 = stable_id("obj2", "exact", prefix="evidence")
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration with UniqueDraftClaimText12345.", [eid1])],
        reviews=[
            make_review(
                mappings={"c1": ["point.1"]},
                missing=["point.2"],
                reason="ReviewReasonPfluegerRequired",
            ),
            make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[]),
        ],
        revisions=[make_claim("c2", "point.2", "Track filtering in fillData via successfullyPassedFilters.", [eid2])],
    )
    a = make_agent(tmp_path, vertex=v)
    a._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert len(a.retriever.collect_calls) == 1
    query, _ = a.retriever.collect_calls[0]
    assert "req_gold_source_pflueger" not in query
    assert "ReviewReasonPfluegerRequired" not in query
    assert "Gold" not in query


def test_t7_invalid_point_ids_or_unevaluable_coverage_suppresses_e3(tmp_path: Path) -> None:
    """T7: Invalid missing point IDs or unevaluable review suppresses E3."""
    # 7a: Unknown missing point ID
    v1 = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.")],
        reviews=[make_review(mappings={"c1": ["point.1"]}, missing=["unknown.point.999"])],
    )
    a1 = make_agent(tmp_path, vertex=v1)
    out1 = a1._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert a1.retriever.collect_calls == []
    assert out1["diagnostics"]["e3_trace"]["triggered"] is False
    assert out1["diagnostics"]["e3_trace"]["trigger_reason"] in {"unknown_answer_point_id", "coverage_review_structural_error"}

    # 7b: Global review failure / unevaluable
    v2 = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.")],
        reviews=[make_review(supported=False, mappings={}, missing=[], unsupported=[], reason="total failure")],
    )
    a2 = make_agent(tmp_path, vertex=v2)
    out2 = a2._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert a2.retriever.collect_calls == []
    assert out2["diagnostics"]["e3_trace"]["triggered"] is False


def test_t8_original_plan_preserved_no_prose_reanalysis(tmp_path: Path) -> None:
    """T8: Original plan constraints are preserved into E3, and version conflicts suppress E3."""
    # 8a: Original plan constraints preserved
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.")],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[]),
        ],
    )
    a = make_agent(tmp_path, vertex=v)
    a.retriever.bundle["plan"]["symbols"] = ["PndPidCorrelator"]
    a.retriever.bundle["plan"]["target_repositories"] = ["pandaroot"]
    a._run_detailed(QUESTION, mode="runtime_e1_v2")
    _, plan = a.retriever.collect_calls[0]
    assert plan.symbols == ["PndPidCorrelator"]
    assert plan.target_repositories == ["pandaroot"]

    # 8b: Version conflict suppresses E3
    b_conflict = bundle_for([make_evidence("obj1")], conflicts=["pandaroot version conflict"])
    b_conflict["plan"]["source_budgets"] = {"code": 1.0}
    b_conflict["candidate_snapshot"] = {"pass_origin": "initial", "rankings": {"exact": [make_evidence("obj1")]}}
    r_conflict = FakeE3Retriever(initial_bundle=b_conflict)
    a_conflict = make_agent(tmp_path, retriever=r_conflict)
    out_conflict = a_conflict._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert r_conflict.collect_calls == []
    assert out_conflict["result"]["status"] == QAStatus.VERSION_CONFLICT


def test_t9_multiple_missing_points_merged_single_query(tmp_path: Path) -> None:
    """T9: Multiple missing points merged into one combined query preserving order."""
    q_t9 = "What is the PndPidCorrelator configuration and how are tracks filtered and monitored?"
    v = FakeVertex(
        decomposition=make_proposal(
            ["PndPidCorrelator configuration options.", "Track filtering in fillData.", "Track monitoring logic."],
            [["PndPidCorrelator", "configuration"], ["tracks", "filtered"], ["monitored"]],
        ),
        answers=[make_claim("c2", "point.2", "Track filtering in fillData.")],
        reviews=[
            make_review(mappings={"c2": ["point.2"]}, missing=["point.1", "point.3"]),
            make_review(mappings={"c2": ["point.2"]}, missing=[]),
        ],
    )
    a = make_agent(tmp_path, vertex=v)
    a._run_detailed(q_t9, mode="runtime_e1_v2")
    assert len(a.retriever.collect_calls) == 1
    query, _ = a.retriever.collect_calls[0]
    pos1 = query.find("PndPidCorrelator configuration options.")
    pos3 = query.find("Track monitoring logic.")
    assert pos1 != -1 and pos3 != -1
    assert pos1 < pos3


def test_t10_cross_pass_differing_ranks_both_no_bonus_tie() -> None:
    """T10: Consolidate candidates across passes using best rank per channel, no cross-pass bonus, tie-breaking."""
    # objA: rank 2 in pass 1 exact, rank 1 in pass 2 exact -> best rank = 1
    # objB: rank 1 in pass 1 exact, rank 3 in pass 2 exact -> best rank = 1
    # Both appear in both passes; neither receives any cross-pass bonus, resulting in an exact RRF score tie.
    candA_pass1 = make_evidence("objA", channel="exact")
    candA_pass2 = make_evidence("objA", channel="exact")
    candB_pass1 = make_evidence("objB", channel="exact")
    candB_pass2 = make_evidence("objB", channel="exact")
    candOther = make_evidence("objOther", channel="exact")

    snapshots = [
        {"pass_origin": "initial", "rankings": {"exact": [candB_pass1, candA_pass1]}},
        {"pass_origin": "e3_targeted", "rankings": {"exact": [candA_pass2, candOther, candB_pass2]}},
    ]
    plan = make_plan()

    res = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=snapshots,
    )
    best_ranks = res["best_channel_ranks"]
    # objA best rank in exact is min(2, 1) = 1
    assert best_ranks["objA"]["exact"] == 1
    # objB best rank in exact is min(1, 3) = 1
    assert best_ranks["objB"]["exact"] == 1
    # No pass-multiplicity bonus: RRF formula uses only best_ranks without pass bonus
    # score(objA) == 2.0 / (60 + 1) == score(objB)
    assert res["scores"]["objA"] == res["scores"]["objB"]
    # Fused order breaks tie deterministically by object_id lexicographical order ("objA" < "objB")
    assert res["fused_candidate_ids"][0] == "objA"
    assert res["fused_candidate_ids"][1] == "objB"


def test_t11_strong_initial_evidence_survives_global_selection() -> None:
    """T11: Strong initial evidence survives global candidate reconsideration and selection."""
    e_init = make_evidence("obj_init", channel="exact")
    e_targeted = make_evidence("obj_targeted", channel="dense")

    snapshots = [
        {"pass_origin": "initial", "rankings": {"exact": [e_init]}},
        {"pass_origin": "e3_targeted", "rankings": {"dense": [e_targeted]}},
    ]
    plan = make_plan()

    res = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=snapshots,
        current_selected_evidence=[e_init],
    )
    selected_oids = [item["object_id"] for item in res["selected_evidence"]]
    assert "obj_init" in selected_oids


def test_t12_useful_targeted_evidence_enters_final_selection() -> None:
    """T12: Useful targeted evidence enters final selection and records newly_admitted_object_ids."""
    e_init = make_evidence("obj_init", channel="exact")
    e_targeted = make_evidence("obj_targeted", channel="exact")

    snapshots = [
        {"pass_origin": "initial", "rankings": {"exact": [e_init]}},
        {"pass_origin": "e3_targeted", "rankings": {"exact": [e_targeted]}},
    ]
    plan = make_plan()

    res = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=snapshots,
        current_selected_evidence=[e_init],
    )
    assert "obj_targeted" in res["newly_admitted_object_ids"]
    assert res["status"] == "success"


def test_t13_payload_consistency_failure_aborts_update() -> None:
    """T13: Inconsistent payload across passes triggers consistency failure on content, ignoring scores/channels."""
    plan = make_plan()

    # 1. source_id mismatch
    e1 = make_evidence("objA", source_id="pandaroot")
    e2 = make_evidence("objA", source_id="luminosityfit")
    res = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=[
            {"pass_origin": "initial", "rankings": {"exact": [e1]}},
            {"pass_origin": "e3_targeted", "rankings": {"exact": [e2]}},
        ],
        current_selected_evidence=[e1],
    )
    assert res["status"] == "consistency_failure"
    assert any("source_id" in f for f in res["consistency_failures"])

    # 2. text mismatch
    e_text1 = make_evidence("objB", text="Version 1 text")
    e_text2 = make_evidence("objB", text="Version 2 text")
    res_text = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=[
            {"pass_origin": "initial", "rankings": {"exact": [e_text1]}},
            {"pass_origin": "e3_targeted", "rankings": {"exact": [e_text2]}},
        ],
    )
    assert res_text["status"] == "consistency_failure"
    assert any("text mismatch" in f for f in res_text["consistency_failures"])

    # 3. object_type mismatch
    e_type1 = dict(make_evidence("objC"), object_type="source_file")
    e_type2 = dict(make_evidence("objC"), object_type="header_file")
    res_type = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=[
            {"pass_origin": "initial", "rankings": {"exact": [e_type1]}},
            {"pass_origin": "e3_targeted", "rankings": {"exact": [e_type2]}},
        ],
    )
    assert res_type["status"] == "consistency_failure"
    assert any("object_type" in f for f in res_type["consistency_failures"])

    # 4. Differing score and retrieval_channels should NOT trigger consistency failure
    e_score1 = make_evidence("objD", score=0.5, channel="exact")
    e_score2 = make_evidence("objD", score=0.9, channel="dense")
    e_score2["retrieval_channels"] = ["exact", "dense"]
    res_score = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=[
            {"pass_origin": "initial", "rankings": {"exact": [e_score1]}},
            {"pass_origin": "e3_targeted", "rankings": {"dense": [e_score2]}},
        ],
    )
    assert res_score["status"] == "success"
    assert res_score.get("consistency_failures", []) == []


def test_t14_retained_support_claim_survival_and_new_claim_rejection(tmp_path: Path) -> None:
    """T14: Unchanged supported claim survives citation displacement via ledger; new claim citing ledger rejected."""
    e1 = make_evidence("obj1", path="src/PndPidCorrelator1.cxx", text="void PndPidCorrelator::Init() {}")
    e2 = make_evidence("obj2", path="src/PndPidCorrelator2.cxx", text="void PndPidCorrelator::fillData() { successfullyPassedFilters(); }")

    # Pass 1 select e1. In pass 2, e2 displaces e1 in the selection
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator config.", [e1["evidence_id"]])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),  # First review: c1 supported
            make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[]),  # Second review
        ],
        revisions=[
            make_claim("c2", "point.2", "Track filtering in fillData via successfullyPassedFilters.", [e2["evidence_id"]]),
        ],
    )

    class DisplacingRetriever(FakeE3Retriever):
        def consolidate_and_select_candidates(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            return {
                "status": "success",
                "selected_evidence": [e2],  # e1 displaced, only e2 selected!
                "newly_admitted_object_ids": ["obj2"],
                "displaced_evidence_ids": [e1["evidence_id"]],
                "fused_candidate_ids": ["obj2", "obj1"],
                "reranked_object_ids": ["obj2"],
                "ranked_object_ids": ["obj2"],
                "best_channel_ranks": {"obj1": {"exact": 2}, "obj2": {"exact": 1}},
                "scores": {"obj1": 0.5, "obj2": 1.0},
                "payloads": {"obj1": e1, "obj2": e2},
                "pass_occurrences": {},
                "failure_reason": None,
            }

    b1 = bundle_for([e1])
    b1["plan"]["source_budgets"] = {"code": 1.0}
    r = DisplacingRetriever(
        initial_bundle=b1,
        targeted_candidates={"exact": [e2]},
    )
    a = make_agent(tmp_path, vertex=v, retriever=r)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")

    # c1 cited e1 which was displaced, but c1 survived because of retained_support_evidence!
    result = out["result"]
    assert result["status"] == QAStatus.ANSWERED
    c1_present = any(c["claim_id"] == "c1" for c in result["claims"])
    assert c1_present

    # Evidence in final QAResult includes both cited items (e1 from ledger, e2 from new selection)
    cited_eids = {item["evidence_id"] for item in result["evidence"]}
    assert e1["evidence_id"] in cited_eids
    assert e2["evidence_id"] in cited_eids

    # Now verify that a NEW or modified claim cannot cite e1 (ledger-only)
    v_illegal = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator config.", [e1["evidence_id"]])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"], "c_illegal": ["point.2"]}, missing=[]),
        ],
        revisions=[
            # c_illegal is a NEW claim citing e1 which is not in bundle["evidence"]!
            make_claim("c_illegal", "point.2", "Illegal claim citing displaced evidence.", [e1["evidence_id"]]),
        ],
    )
    b_illegal = bundle_for([e1])
    b_illegal["plan"]["source_budgets"] = {"code": 1.0}
    r_illegal = DisplacingRetriever(initial_bundle=b_illegal, targeted_candidates={"exact": [e2]})
    a_illegal = make_agent(tmp_path, vertex=v_illegal, retriever=r_illegal)
    out_illegal = a_illegal._run_detailed(QUESTION, mode="runtime_e1_v2")
    # c_illegal must have verification error "invalid evidence for c_illegal"
    assert any("invalid evidence for c_illegal" in err for err in out_illegal["result"]["verification_errors"])


def test_t15_revision_count_bounded_at_most_one(tmp_path: Path) -> None:
    """T15: revision_count is hard-bounded to <= 1 across the full workflow."""
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "Initial claim.")],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),  # Second review still missing!
        ],
        revisions=[make_claim("c2", "point.2", "Revised claim.")],
    )
    a = make_agent(tmp_path, vertex=v)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert out["diagnostics"]["revision_count"] == 1


def test_t16_missing_point_retrieval_count_consumed_before_external_calls(tmp_path: Path) -> None:
    """T16: missing_point_retrieval_count is strictly hard-bounded to <= 1."""
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "Initial claim.")],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"]}, missing=[]),
        ],
    )
    a = make_agent(tmp_path, vertex=v)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    trace = out["diagnostics"]["e3_trace"]
    assert trace["missing_point_retrieval_count"] == 1


def test_t17_second_verify_cannot_trigger_another_e3(tmp_path: Path) -> None:
    """T17: Second verify pass cannot trigger another E3 retrieval attempt."""
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "Initial claim.")],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),  # Pass 1
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),  # Pass 2: still missing!
        ],
        revisions=[make_claim("c2", "point.2", "Revised claim.")],
    )
    a = make_agent(tmp_path, vertex=v)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert len(a.retriever.collect_calls) == 1  # Exactly 1, never 2
    assert out["diagnostics"]["e3_trace"]["missing_point_retrieval_count"] == 1


def test_t18_empty_or_no_gain_retains_prior_bundle(tmp_path: Path) -> None:
    """T18: Empty or no-gain targeted collection retains prior bundle and terminates honestly."""
    e1 = make_evidence("obj1", path="src/PndPidCorrelator1.cxx", text="void PndPidCorrelator::Init() {}")
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "Initial claim.", [e1["evidence_id"]])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
        ],
    )
    # Targeted collection returns no candidates
    r = FakeE3Retriever(
        initial_bundle=bundle_for([e1]),
        targeted_candidates={},
    )
    a = make_agent(tmp_path, vertex=v, retriever=r)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    trace = out["diagnostics"]["e3_trace"]
    assert trace["no_gain"] is True
    # Prior evidence was retained
    assert [e["evidence_id"] for e in out["diagnostics"]["selected_evidence"]] == [e1["evidence_id"]]


def test_t19_public_qa_dto_schema_invariant(tmp_path: Path) -> None:
    """T19: Public QAResult schema remains strictly invariant; no internal E3 metadata leaked."""
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "Config.")],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[]),
        ],
    )
    a = make_agent(tmp_path, vertex=v)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    result_dict = out["result"]

    # Validate with Pydantic model
    validated = QAResult.model_validate(result_dict)
    assert set(result_dict.keys()) == set(QAResult.model_fields.keys())
    for claim in result_dict["claims"]:
        assert set(claim.keys()) == {"claim_id", "claim_text", "evidence_ids"}
        assert "answer_point_ids" not in claim
        assert "declared_answer_point_ids" not in claim


def test_t20_default_answer_point_mode_legacy() -> None:
    """T20: DEFAULT_ANSWER_POINT_MODE remains legacy_question_core."""
    assert DEFAULT_ANSWER_POINT_MODE == "legacy_question_core"


# ---------------------------------------------------------------------------
# Sentinels
# ---------------------------------------------------------------------------

def test_sentinel_1_rerank_original_question_only_targeted_collection_combined(tmp_path: Path) -> None:
    """Sentinel 1: Global reranker receives original question ONLY; targeted collection receives combined objective."""
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    eid2 = stable_id("obj2", "exact", prefix="evidence")
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.", [eid1])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[]),
        ],
        revisions=[make_claim("c2", "point.2", "Track filtering in fillData via successfullyPassedFilters.", [eid2])],
    )
    a = make_agent(tmp_path, vertex=v)
    a._run_detailed(QUESTION, mode="runtime_e1_v2")

    # Check targeted collection query: contains missing point aspect
    assert len(a.retriever.collect_calls) == 1
    collection_query, _ = a.retriever.collect_calls[0]
    assert "Target missing question aspects:" in collection_query

    # Check consolidation call: receives original question ONLY
    assert len(a.retriever.consolidate_calls) == 1
    consolidate_arg = a.retriever.consolidate_calls[0]["original_question"]
    assert consolidate_arg == QUESTION
    assert "Target missing question aspects:" not in consolidate_arg


def test_sentinel_2_targeted_collection_local_rerank_zero_global_rerank_one(tmp_path: Path) -> None:
    """Sentinel 2: E3 targeted collection local reranker calls = 0; single global rerank call = 1."""
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    eid2 = stable_id("obj2", "exact", prefix="evidence")
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.", [eid1])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[]),
        ],
        revisions=[make_claim("c2", "point.2", "Track filtering in fillData via successfullyPassedFilters.", [eid2])],
    )
    a = make_agent(tmp_path, vertex=v)
    a._run_detailed(QUESTION, mode="runtime_e1_v2")

    # Count rerank calls in vertex
    rerank_calls = [c for c in v.calls if c[0].get("task") == "rerank_evidence"]
    assert len(rerank_calls) == 1


def test_sentinel_3_initial_pass_candidate_capture_no_duplicate_calls() -> None:
    """Sentinel 3: Real Retriever.retrieve candidate capture incurs no duplicate channel calls; sidecar-only difference."""
    retriever = Retriever.__new__(Retriever)
    vertex = FakeVertex(rerank_order=["obj1"])
    retriever.vertex = vertex
    retriever.policies = SimpleNamespace(
        candidate_pool_per_channel=10,
        final_evidence_limit=12,
        max_relation_hops=2,
    )
    retriever._source_type = lambda payload: "code"
    retriever.analyze = lambda q, **kwargs: make_plan()
    retriever.query_expansions = SimpleNamespace(rules=[])

    channel_calls: list[tuple[str, Any, int]] = []

    def fake_collect_channel_rankings(question: str, plan: Any, limit: int) -> tuple[dict[str, list[dict[str, Any]]], Any, Any]:
        channel_calls.append((question, plan, limit))
        ev = make_evidence("obj1", channel="exact")
        rankings = {"exact": [ev], "dense": [], "sparse": [], "paper": [], "workflow": [], "graph": []}
        semantic_query = SimpleNamespace(
            text="test question",
            intent="general",
            symbols=[],
            as_dict=lambda: {"intent": "general", "symbols": []},
        )
        return rankings, semantic_query, [0.1, 0.2]

    retriever._collect_channel_rankings = fake_collect_channel_rankings

    # Call 1: capture_candidates=False
    bundle_normal = retriever.retrieve("test question", capture_candidates=False)
    count_after_1 = len(channel_calls)
    assert count_after_1 == 1

    # Call 2: capture_candidates=True
    bundle_captured = retriever.retrieve("test question", capture_candidates=True)
    count_after_2 = len(channel_calls)
    assert count_after_2 == 2  # Exactly 1 channel call per retrieve, zero duplicate calls!

    # Sidecar-only difference
    assert "candidate_snapshot" not in bundle_normal
    assert "candidate_snapshot" in bundle_captured
    bundle_captured_stripped = {k: v for k, v in bundle_captured.items() if k != "candidate_snapshot"}
    assert bundle_normal == bundle_captured_stripped


# ---------------------------------------------------------------------------
# Defect Verifications & Acceptance Regressions
# ---------------------------------------------------------------------------

def test_missing_point_retrieve_consumes_attempt_before_collection_and_catches_exception(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Defect 1: State attempt consumed before external calls; collection exception caught with zero retry."""
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.", [eid1])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
        ],
    )
    b = bundle_for([make_evidence("obj1")])
    b["plan"]["source_budgets"] = {"code": 1.0}
    b["candidate_snapshot"] = {"pass_origin": "initial", "rankings": {"exact": [make_evidence("obj1")]}}

    captured_states: list[dict[str, Any]] = []
    real_mpr = QAAgent._missing_point_retrieve
    def tracking_mpr(self: Any, state: Any) -> Any:
        captured_states.append(state)
        return real_mpr(self, state)
    monkeypatch.setattr(QAAgent, "_missing_point_retrieve", tracking_mpr)

    class RaisingCollectRetriever(FakeE3Retriever):
        def collect_channel_candidates(self, question: str, plan: Any = None) -> dict[str, list[dict[str, Any]]]:
            self.collect_calls.append((question, plan))
            # Assert state attempt was consumed BEFORE external collection runs
            assert len(captured_states) == 1
            assert captured_states[0].get("missing_point_retrieval_count") == 1
            raise RuntimeError("simulated collection failure")

    r = RaisingCollectRetriever(initial_bundle=b, vertex=v)
    a = make_agent(tmp_path, vertex=v, retriever=r)

    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert len(r.collect_calls) == 1  # Called once, zero retry
    assert not hasattr(a, "_current_state")
    trace = out["diagnostics"]["e3_trace"]
    assert trace["missing_point_retrieval_count"] == 1
    assert trace["atomic_update_status"] == "failure"
    assert trace["no_gain"] is True
    assert "simulated collection failure" in trace["failure_reason"]
    # Graph continued to finalize honestly
    assert out["result"]["status"] in {QAStatus.ANSWERED, QAStatus.INSUFFICIENT_EVIDENCE}


def test_missing_point_retrieve_consumes_attempt_before_consolidation_and_catches_exception(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Defect 1: State attempt consumed before consolidation; selector exception caught with zero retry."""
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "PndPidCorrelator configuration.", [eid1])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
        ],
    )
    b = bundle_for([make_evidence("obj1")])
    b["plan"]["source_budgets"] = {"code": 1.0}
    b["candidate_snapshot"] = {"pass_origin": "initial", "rankings": {"exact": [make_evidence("obj1")]}}

    captured_states: list[dict[str, Any]] = []
    real_mpr = QAAgent._missing_point_retrieve
    def tracking_mpr(self: Any, state: Any) -> Any:
        captured_states.append(state)
        return real_mpr(self, state)
    monkeypatch.setattr(QAAgent, "_missing_point_retrieve", tracking_mpr)

    class RaisingConsolidateRetriever(FakeE3Retriever):
        def consolidate_and_select_candidates(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            self.consolidate_calls.append(kwargs)
            # Assert state attempt was consumed BEFORE external consolidation runs
            assert len(captured_states) == 1
            assert captured_states[0].get("missing_point_retrieval_count") == 1
            raise RuntimeError("simulated rerank/selection failure")

    r = RaisingConsolidateRetriever(
        initial_bundle=b,
        targeted_candidates={"exact": [make_evidence("obj2")]},
        vertex=v,
    )
    a = make_agent(tmp_path, vertex=v, retriever=r)

    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    assert len(r.collect_calls) == 1
    assert len(r.consolidate_calls) == 1
    assert not hasattr(a, "_current_state")
    trace = out["diagnostics"]["e3_trace"]
    assert trace["missing_point_retrieval_count"] == 1
    assert trace["atomic_update_status"] == "failure"
    assert trace["no_gain"] is True
    assert "simulated rerank/selection failure" in trace["failure_reason"]


def test_empty_targeted_candidates_stops_e3_rerank_no_unselected_admitted(tmp_path: Path) -> None:
    """Defect 1: Empty targeted candidates stops E3 consolidation; unselected pass-1 candidates are never admitted."""
    e1 = make_evidence("obj1", path="src/PndPidCorrelator1.cxx")
    e_unselected = make_evidence("obj_unselected", path="src/PndPidCorrelatorUnselected.cxx")
    b = bundle_for([e1])
    b["plan"]["source_budgets"] = {"code": 1.0}
    b["candidate_snapshot"] = {
        "pass_origin": "initial",
        "rankings": {"exact": [deepcopy(e1), deepcopy(e_unselected)]},
    }
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "Initial claim.", [eid1])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
        ],
    )
    r = FakeE3Retriever(
        initial_bundle=b,
        targeted_candidates={"exact": []},  # Empty targeted candidates!
        vertex=v,
    )
    a = make_agent(tmp_path, vertex=v, retriever=r)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    # Assert consolidate_and_select_candidates was NOT called
    assert len(r.consolidate_calls) == 0
    trace = out["diagnostics"]["e3_trace"]
    assert trace["atomic_update_status"] == "no_gain"
    assert trace["no_gain"] is True
    assert trace["failure_reason"] == "empty_targeted_candidates"
    # e_unselected was NOT admitted!
    selected_oids = [e.get("object_id") for e in out["diagnostics"]["selected_evidence"]]
    assert "obj_unselected" not in selected_oids
    assert selected_oids == ["obj1"]


def test_legacy_and_shadow_zero_snapshot_leakage(tmp_path: Path) -> None:
    """Defect 2: Legacy and shadow modes have zero snapshot leakage on bundle or state."""
    a = make_agent(tmp_path)
    out_legacy = a.run_detailed(QUESTION)
    assert a.retriever.retrieve_calls[0][2] is False
    assert "e3_trace" not in out_legacy["diagnostics"]

    a_shadow = make_agent(tmp_path)
    out_shadow = a_shadow.run_answer_point_coverage_diagnostic(QUESTION)
    assert a_shadow.retriever.retrieve_calls[0][2] is False
    assert "e3_trace" not in out_shadow["diagnostics"]


def test_missing_snapshot_in_runtime_fails_honestly(tmp_path: Path) -> None:
    """Defect 2: Missing snapshot in runtime_e1_v2 fails honestly without fabricating snapshots."""
    e1 = make_evidence("obj1")
    b = bundle_for([e1])
    b["plan"]["source_budgets"] = {"code": 1.0}
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "Config.", [e1["evidence_id"]])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
        ],
    )

    class NoSnapshotRetriever(FakeE3Retriever):
        def retrieve(self, question: str, plan: Any = None, capture_candidates: bool = False) -> dict[str, Any]:
            self.retrieve_calls.append((question, plan, capture_candidates))
            bundle = deepcopy(self.bundle)
            bundle.pop("candidate_snapshot", None)
            return bundle

    r = NoSnapshotRetriever(initial_bundle=b, targeted_candidates={"exact": [make_evidence("obj2")]}, vertex=v)
    a = make_agent(tmp_path, vertex=v, retriever=r)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    trace = out["diagnostics"]["e3_trace"]
    assert trace["atomic_update_status"] == "failure"
    assert "missing candidate snapshot from initial pass" in trace["failure_reason"]
    assert trace["no_gain"] is True
    # Collection must NOT have been called because missing snapshot detection happened before collection
    assert len(r.collect_calls) == 0


def test_direct_missing_point_retrieve_attempt_consumption_and_return_count(tmp_path: Path) -> None:
    """Verify direct _missing_point_retrieve assigns count=1 to state before work and returns count=1."""
    a = make_agent(tmp_path)
    state: dict[str, Any] = {
        "question": QUESTION,
        "missing_point_retrieval_count": 0,
        "missing_answer_point_ids": ["point.2"],
        "runtime_answer_points": POINTS,
        "bundle": {"evidence": [], "plan": {}},
        "candidate_snapshots": [],
        "answer_point_coverage_mode": "runtime_e1_v2",
    }
    res = a._missing_point_retrieve(state)
    # State counter was assigned
    assert state.get("missing_point_retrieval_count") == 1
    # Returned dict has counter
    assert res.get("missing_point_retrieval_count") == 1
    assert not hasattr(a, "_current_state")


def test_direct_missing_point_retrieve_collection_attempt_consumption_closure(tmp_path: Path) -> None:
    """Verify direct _missing_point_retrieve consumes state attempt count=1 before collection runs via closure."""
    state: dict[str, Any] = {
        "question": QUESTION,
        "missing_point_retrieval_count": 0,
        "missing_answer_point_ids": ["point.2"],
        "runtime_answer_points": POINTS,
        "bundle": bundle_for([make_evidence("obj1")]),
        "candidate_snapshots": [{"pass_origin": "initial", "rankings": {"exact": [make_evidence("obj1")]}}],
        "answer_point_coverage_mode": "runtime_e1_v2",
    }
    class RaisingClosureRetriever(FakeE3Retriever):
        def collect_channel_candidates(self, question: str, plan: Any = None) -> dict[str, list[dict[str, Any]]]:
            # Fake closure referencing state directly: assert state count == 1
            assert state.get("missing_point_retrieval_count") == 1
            raise RuntimeError("collection failure")

    r = RaisingClosureRetriever(initial_bundle=state["bundle"], vertex=FakeVertex())
    a = make_agent(tmp_path, retriever=r)
    res = a._missing_point_retrieve(state)
    assert state.get("missing_point_retrieval_count") == 1
    assert res.get("missing_point_retrieval_count") == 1
    assert not hasattr(a, "_current_state")


def test_direct_missing_point_retrieve_consolidation_attempt_consumption_closure(tmp_path: Path) -> None:
    """Verify direct _missing_point_retrieve consumes state attempt count=1 before consolidation runs via closure."""
    state: dict[str, Any] = {
        "question": QUESTION,
        "missing_point_retrieval_count": 0,
        "missing_answer_point_ids": ["point.2"],
        "runtime_answer_points": POINTS,
        "bundle": bundle_for([make_evidence("obj1")]),
        "candidate_snapshots": [{"pass_origin": "initial", "rankings": {"exact": [make_evidence("obj1")]}}],
        "answer_point_coverage_mode": "runtime_e1_v2",
    }
    class RaisingClosureRetriever(FakeE3Retriever):
        def consolidate_and_select_candidates(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
            # Fake closure referencing state directly: assert state count == 1
            assert state.get("missing_point_retrieval_count") == 1
            raise RuntimeError("consolidation failure")

    r = RaisingClosureRetriever(
        initial_bundle=state["bundle"],
        targeted_candidates={"exact": [make_evidence("obj2")]},
        vertex=FakeVertex(),
    )
    a = make_agent(tmp_path, retriever=r)
    res = a._missing_point_retrieve(state)
    assert state.get("missing_point_retrieval_count") == 1
    assert res.get("missing_point_retrieval_count") == 1
    assert not hasattr(a, "_current_state")


def test_retrieve_type_error_propagates_without_catch_and_retry(tmp_path: Path) -> None:
    """Verify internal TypeError in retriever.retrieve is NOT caught and retried, called exactly once."""
    class RaisingTypeRetriever:
        def __init__(self) -> None:
            self.calls = 0

        def retrieve(self, question: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
            self.calls += 1
            raise TypeError("internal type error inside provider")

    retriever = RaisingTypeRetriever()
    agent = QAAgent(tmp_path, retriever=retriever, vertex=FakeVertex())

    # 1. runtime_e1_v2 mode propagates TypeError directly, called exactly once
    with pytest.raises(TypeError, match="internal type error inside provider"):
        agent._retrieve({"question": QUESTION, "answer_point_coverage_mode": "runtime_e1_v2"})
    assert retriever.calls == 1

    # 2. legacy mode also propagates TypeError directly, called exactly once
    retriever.calls = 0
    with pytest.raises(TypeError, match="internal type error inside provider"):
        agent._retrieve({"question": QUESTION, "answer_point_coverage_mode": "legacy_question_core"})
    assert retriever.calls == 1


def test_targeted_retrieve_type_error_propagates_without_catch_and_retry(tmp_path: Path) -> None:
    """Verify internal TypeError in _targeted_retrieve is NOT caught and retried, called exactly once."""
    class RaisingTypeRetriever:
        def __init__(self) -> None:
            self.calls = 0

        def retrieve(self, question: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
            self.calls += 1
            raise TypeError("internal type error inside provider")

    retriever = RaisingTypeRetriever()
    agent = QAAgent(tmp_path, retriever=retriever, vertex=FakeVertex())
    b = bundle_for([make_evidence("obj1")])
    b["plan"]["source_budgets"] = {"code": 1.0}
    state: dict[str, Any] = {
        "question": QUESTION,
        "bundle": b,
        "errors": [],
        "answer_point_coverage_mode": "runtime_e1_v2",
    }
    with pytest.raises(TypeError, match="internal type error inside provider"):
        agent._targeted_retrieve(state)
    assert retriever.calls == 1

    # Legacy mode
    retriever.calls = 0
    state_legacy = dict(state, answer_point_coverage_mode="legacy_question_core")
    with pytest.raises(TypeError, match="internal type error inside provider"):
        agent._targeted_retrieve(state_legacy)
    assert retriever.calls == 1


def test_legacy_and_shadow_retrieve_signature_has_no_capture_candidates_kwarg(tmp_path: Path) -> None:
    """Verify legacy and shadow modes invoke retrieve without capture_candidates kwarg at all."""
    calls_kwargs: list[dict[str, Any]] = []

    b = bundle_for([make_evidence("obj1")])
    b["plan"]["source_budgets"] = {"code": 1.0}

    class StrictSignatureRetriever:
        def __init__(self) -> None:
            self.bundle = b

        def retrieve(self, question: str, plan: Any = None, **kwargs: Any) -> dict[str, Any]:
            calls_kwargs.append(kwargs)
            return self.bundle

    retriever = StrictSignatureRetriever()
    agent = QAAgent(tmp_path, retriever=retriever, vertex=FakeVertex())

    # Legacy retrieve
    agent._retrieve({"question": QUESTION, "answer_point_coverage_mode": "legacy_question_core"})
    assert "capture_candidates" not in calls_kwargs[-1]

    # Legacy targeted retrieve
    state = {
        "question": QUESTION,
        "bundle": b,
        "errors": [],
        "answer_point_coverage_mode": "legacy_question_core",
    }
    agent._targeted_retrieve(state)
    assert "capture_candidates" not in calls_kwargs[-1]

    # Runtime retrieve must pass capture_candidates=True
    agent._retrieve({"question": QUESTION, "answer_point_coverage_mode": "runtime_e1_v2"})
    assert calls_kwargs[-1].get("capture_candidates") is True

    # Runtime targeted retrieve must pass capture_candidates=True
    state_runtime = dict(state, answer_point_coverage_mode="runtime_e1_v2")
    agent._targeted_retrieve(state_runtime)
    assert calls_kwargs[-1].get("capture_candidates") is True


def test_finalize_preserves_bundle_evidence_order_and_appends_retained_support(tmp_path: Path) -> None:
    """Defect 3: _finalize preserves original bundle list order and appends retained support deterministically."""
    ev_B = make_evidence("objB", path="src/B.cxx")
    ev_A = make_evidence("objA", path="src/A.cxx")
    ev_C = make_evidence("objC", path="src/C.cxx")
    ret_2 = make_evidence("objRet2", path="src/Ret2.cxx")
    ret_1 = make_evidence("objRet1", path="src/Ret1.cxx")

    ev_B["evidence_id"] = "ev_B"
    ev_A["evidence_id"] = "ev_A"
    ev_C["evidence_id"] = "ev_C"
    ret_2["evidence_id"] = "ret_2"
    ret_1["evidence_id"] = "ret_1"

    claims = [
        {"claim_id": "c1", "claim_text": "Claim 1", "evidence_ids": ["ev_A", "ret_2"]},
        {"claim_id": "c2", "claim_text": "Claim 2", "evidence_ids": ["ev_B", "ret_1"]},
    ]

    state: dict[str, Any] = {
        "question": QUESTION,
        "sufficient": True,
        "bundle": {
            "plan": {"resolved_versions": {}},
            "evidence": [ev_B, ev_A, ev_C],  # Specific order: B, A, C
        },
        "supported_claims": claims,
        "retained_support_evidence": {
            "ret_2": ret_2,
            "ret_1": ret_1,
        },
        "answer_point_coverage_mode": "runtime_e1_v2",
        "runtime_answer_points": [
            {"answer_point_id": "point.1", "text": "Point 1"},
            {"answer_point_id": "point.2", "text": "Point 2"},
        ],
        "errors": [],
    }

    agent = make_agent(tmp_path)
    res_runtime = agent._finalize(state)
    cited_eids_runtime = [item["evidence_id"] for item in res_runtime["result"]["evidence"]]
    # Bundle order [ev_B, ev_A] strictly preserved, retained support appended deterministically by sorted ID
    assert cited_eids_runtime == ["ev_B", "ev_A", "ret_1", "ret_2"]

    # Legacy mode does not append retained support
    state_legacy = dict(state)
    state_legacy["answer_point_coverage_mode"] = "legacy_question_core"
    res_legacy = agent._finalize(state_legacy)
    cited_eids_legacy = [item["evidence_id"] for item in res_legacy["result"]["evidence"]]
    assert cited_eids_legacy == ["ev_B", "ev_A"]


def test_plan_source_budgets_not_fabricated() -> None:
    """Defect 4: Original plan source constraints preserved without fabricating source_budgets: {'code': 1.0}."""
    plan = make_plan(source_budgets={"paper": 1.0})
    e = make_evidence("objPaper", channel="exact")
    e["source_id"] = "li_2026"
    e["object_type"] = "thesis_section"

    res = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=[{"pass_origin": "initial", "rankings": {"exact": [e]}}],
    )
    assert res["status"] == "success"
    # Verify plan was not mutated to add {"code": 1.0}
    assert plan.source_budgets == {"paper": 1.0}


def test_prioritize_and_select_evidence_seam_shared_and_exact_order_from_best_ranks() -> None:
    """Defect 5: Seam extracted and exact candidate ordering derived from global best channel ranks."""
    assert hasattr(Retriever, "_prioritize_and_select_evidence")

    # objX: exact rank 2 in pass 1, rank 3 in pass 2 -> best rank 2
    # objY: exact rank 5 in pass 1, rank 1 in pass 2 -> best rank 1
    # Global exact candidate order should place objY before objX based on best rank
    evX = make_evidence("objX", channel="exact")
    evY = make_evidence("objY", channel="exact")

    snapshots = [
        {"pass_origin": "initial", "rankings": {"exact": [evX, evY]}},
        {"pass_origin": "e3_targeted", "rankings": {"exact": [evY, evX]}},
    ]
    plan = make_plan()

    res = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=snapshots,
    )
    assert res["status"] == "success"
    assert res["best_channel_ranks"]["objY"]["exact"] == 1
    assert res["best_channel_ranks"]["objX"]["exact"] == 1 or res["best_channel_ranks"]["objX"]["exact"] == 2


def test_pass_occurrences_compact_provenance_format() -> None:
    """Defect 6: Trace records compact pass_occurrences without payload bulk."""
    e1 = make_evidence("objA", channel="exact")
    snapshots = [
        {"pass_origin": "initial", "rankings": {"exact": [e1]}},
        {"pass_origin": "e3_targeted", "rankings": {"dense": [make_evidence("objA", channel="dense")]}},
    ]
    plan = make_plan()

    res = Retriever.consolidate_and_select_candidates(
        DummyRetriever(),
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=snapshots,
    )
    occ = res["pass_occurrences"]["objA"]
    assert len(occ) == 2
    assert occ[0] == {"pass_origin": "initial", "channel": "exact", "rank": 1}
    assert occ[1] == {"pass_origin": "e3_targeted", "channel": "dense", "rank": 1}
    for entry in occ:
        assert set(entry.keys()) == {"pass_origin", "channel", "rank"}


def test_recovery_accounting_gated_to_second_review(tmp_path: Path) -> None:
    """Defect 6: Recovery accounting only runs on evaluable second review (revision_count >= 1)."""
    eid1 = stable_id("obj1", "exact", prefix="evidence")
    eid2 = stable_id("obj2", "exact", prefix="evidence")
    v = FakeVertex(
        answers=[make_claim("c1", "point.1", "Initial.", [eid1])],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),  # First review (revision_count=0)
            make_review(mappings={"c1": ["point.1"], "c2": ["point.2"]}, missing=[]),  # Second review (revision_count=1)
        ],
        revisions=[make_claim("c2", "point.2", "Revised.", [eid2])],
    )
    a = make_agent(tmp_path, vertex=v)
    out = a._run_detailed(QUESTION, mode="runtime_e1_v2")
    trace = out["diagnostics"]["e3_trace"]
    assert trace["recovered_on_revision"] is True
    assert trace["recovered_answer_point_ids"] == ["point.2"]
    assert trace["post_retrieval_coverage_evaluable"] is True


def test_claim_matches_retained_exact_structure() -> None:
    """Defect 7: _claim_matches_retained performs exact structured equality without .strip()."""
    base = {
        "claim_id": "c1",
        "claim_text": "Exact text here.",
        "evidence_ids": ["ev1", "ev2"],
        "answer_point_ids": ["p1"],
        "declared_answer_point_ids": ["p1"],
    }
    assert _claim_matches_retained(base, dict(base)) is True

    # Trailing whitespace in text must NOT match
    with_trailing = dict(base, claim_text="Exact text here. ")
    assert _claim_matches_retained(with_trailing, base) is False
    assert _claim_matches_retained(base, with_trailing) is False

    # Changed fields
    assert _claim_matches_retained(dict(base, evidence_ids=["ev1", "ev3"]), base) is False
    assert _claim_matches_retained(dict(base, answer_point_ids=["p2"]), base) is False
    assert _claim_matches_retained(dict(base, declared_answer_point_ids=["p2"]), base) is False


def test_modified_claim_rejected_by_ledger_and_unchanged_claim_fails_normal_version_check(tmp_path: Path) -> None:
    """Defect 7: Modified claim rejected by ledger; unchanged claim fails normal version check."""
    ev_displaced = make_evidence("obj1")
    ev_new = make_evidence("obj2")
    agent = make_agent(tmp_path)

    # 1. Modified claim text citing displaced evidence is rejected
    state_mod_text: dict[str, Any] = {
        "question": QUESTION,
        "bundle": {
            "evidence": [ev_new],
            "plan": {"resolved_versions": {"pandaroot": ev_displaced["source_version_id"].split("@")[1]}},
        },
        "draft": {
            "claims": [
                make_claim("c1", "point.1", "Initial text modified.", [ev_displaced["evidence_id"]]),
            ]
        },
        "retained_supported_claims": [
            make_claim("c1", "point.1", "Initial text.", [ev_displaced["evidence_id"]]),
        ],
        "retained_support_evidence": {
            ev_displaced["evidence_id"]: ev_displaced,
        },
        "answer_point_coverage_mode": "runtime_e1_v2",
        "runtime_answer_points": [{"answer_point_id": "point.1", "text": "Point 1"}],
    }
    v_out_mod_text = agent._verify(state_mod_text)
    assert any("invalid evidence for c1" in err for err in v_out_mod_text["errors"])

    # 2. Modified claim mapping citing displaced evidence is rejected
    state_mod_map: dict[str, Any] = {
        "question": QUESTION,
        "bundle": {
            "evidence": [ev_new],
            "plan": {"resolved_versions": {"pandaroot": ev_displaced["source_version_id"].split("@")[1]}},
        },
        "draft": {
            "claims": [
                make_claim("c1", "point.2", "Initial text.", [ev_displaced["evidence_id"]]),
            ]
        },
        "retained_supported_claims": [
            make_claim("c1", "point.1", "Initial text.", [ev_displaced["evidence_id"]]),
        ],
        "retained_support_evidence": {
            ev_displaced["evidence_id"]: ev_displaced,
        },
        "answer_point_coverage_mode": "runtime_e1_v2",
        "runtime_answer_points": [
            {"answer_point_id": "point.1", "text": "Point 1"},
            {"answer_point_id": "point.2", "text": "Point 2"},
        ],
    }
    v_out_mod_map = agent._verify(state_mod_map)
    assert any("invalid evidence for c1" in err for err in v_out_mod_map["errors"])

    # 3. Unchanged claim citing retained evidence with version conflict fails normal version check
    ev_conflicted = make_evidence("obj1", source_version_id="pandaroot@wrong_version")
    state_conf: dict[str, Any] = {
        "question": QUESTION,
        "bundle": {
            "evidence": [ev_new],
            "plan": {
                "resolved_versions": {"pandaroot": "expected_version"},
            },
        },
        "draft": {
            "claims": [
                make_claim("c1", "point.1", "Initial text.", [ev_conflicted["evidence_id"]]),
            ]
        },
        "retained_supported_claims": [
            make_claim("c1", "point.1", "Initial text.", [ev_conflicted["evidence_id"]]),
        ],
        "retained_support_evidence": {
            ev_conflicted["evidence_id"]: ev_conflicted,
        },
        "answer_point_coverage_mode": "runtime_e1_v2",
        "runtime_answer_points": [{"answer_point_id": "point.1", "text": "Point 1"}],
    }
    v_out_conf = agent._verify(state_conf)
    assert any("wrong code version" in err for err in v_out_conf["errors"])


def test_pre_answer_snapshot_capture_path(tmp_path: Path) -> None:
    """Defect 8: Pre-answer targeted retrieval captures snapshot tagged pre_answer_targeted_N."""
    e1 = make_evidence("obj1")
    e2 = make_evidence("obj2")
    b = bundle_for([e1])
    b["plan"]["source_budgets"] = {"code": 1.0}
    v = FakeVertex()
    r = FakeE3Retriever(initial_bundle=b, targeted_candidates={"exact": [e2]}, vertex=v)
    a = make_agent(tmp_path, vertex=v, retriever=r)

    state: dict[str, Any] = {
        "question": QUESTION,
        "bundle": b,
        "retrieval_count": 0,
        "answer_point_coverage_mode": "runtime_e1_v2",
        "candidate_snapshots": [{"pass_origin": "initial", "rankings": {"exact": [e1]}}],
        "errors": ["missing evidence symbol: PndPidCorrelator"],
    }
    res = a._targeted_retrieve(state)
    assert res["retrieval_count"] == 1
    snapshots = res["candidate_snapshots"]
    assert len(snapshots) == 2
    assert snapshots[1]["pass_origin"] == "pre_answer_targeted_1"

    # Legacy mode must not capture candidate_snapshots
    state_legacy = dict(state)
    state_legacy["answer_point_coverage_mode"] = "legacy_question_core"
    res_legacy = a._targeted_retrieve(state_legacy)
    assert "candidate_snapshots" not in res_legacy


# ---------------------------------------------------------------------------
# E3-A1 Bounded Contract Correction Regressions (Fix 1 & Fix 2)
# ---------------------------------------------------------------------------

def test_e3_real_retriever_methods_saturated_pool_reaches_global_reranker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Correction 1 (Finding 1 & 3): Real Retriever.retrieve + collect_channel_candidates
    + _apply_structured_replacement with saturated >= 30 base pool and initial3 + targeted3
    supplemental candidates all reaching single global reranker with original question."""
    init_base_items = [make_evidence(f"base_{i:02d}", channel="exact") for i in range(32)]
    tgt_base_items = [make_evidence(f"tgt_b_{i:02d}", channel="exact") for i in range(5)]
    init_supp_ids = ["init_s1", "init_s2", "init_s3"]
    tgt_supp_ids = ["tgt_s1", "tgt_s2", "tgt_s3"]

    vertex = FakeVertex(
        answers=[
            make_claim(
                "c1",
                "point.1",
                "Initial draft claim.",
                [stable_id("base_00", "exact", prefix="evidence")],
            )
        ],
        reviews=[
            make_review(mappings={"c1": ["point.1"]}, missing=["point.2"]),
            make_review(mappings={"c1": ["point.1"]}, missing=[]),
        ],
        rerank_order=["init_s1", "tgt_s1", "base_00", "base_01"],
    )

    retriever = Retriever.__new__(Retriever)
    retriever.vertex = vertex
    retriever.policies = SimpleNamespace(
        candidate_pool_per_channel=35,
        final_evidence_limit=12,
        max_relation_hops=2,
    )
    retriever._source_type = lambda payload: "code"
    retriever.analyze = lambda q, **kwargs: make_plan(symbols=["sym1"])
    retriever.query_expansions = SimpleNamespace(
        rules=[SimpleNamespace(rule_id="rule_sr", structured_replacement=True, triggers=["pndpidcorrelator", "what", "target"])]
    )
    retriever.storage = CatalogStorage([])
    retriever.context_sources = None

    channel_calls: list[tuple[str, Any, int]] = []
    def fake_collect_channel_rankings(question: str, plan: Any, limit: int) -> tuple[dict[str, list[dict[str, Any]]], Any, Any]:
        channel_calls.append((question, plan, limit))
        semantic_query = SimpleNamespace(
            text=question, intent="general", symbols=[], as_dict=lambda: {"intent": "general", "symbols": []}
        )
        if len(channel_calls) == 1:
            rankings = {"exact": init_base_items, "dense": [], "sparse": [], "paper": [], "workflow": [], "graph": []}
        else:
            rankings = {"exact": tgt_base_items, "dense": [], "sparse": [], "paper": [], "workflow": [], "graph": []}
        return rankings, semantic_query, [0.1, 0.2]
    retriever._collect_channel_rankings = fake_collect_channel_rankings

    contribution_calls: list[tuple[str, Any]] = []
    def fake_build_contribution(question: str, plan: Any, **kwargs: Any) -> Any:
        contribution_calls.append((question, plan))
        if len(contribution_calls) == 1:
            supp_ids = init_supp_ids
        else:
            supp_ids = tgt_supp_ids
        return SimpleNamespace(
            bridged_payloads={oid: make_evidence(oid) for oid in supp_ids},
            bridge_receipts=[],
            reachability_receipts=[],
            resolution_receipt={},
            candidates=[],
        )
    monkeypatch.setattr("panda_agent.retrieval.build_structured_contribution_from_storage", fake_build_contribution)

    def fake_select_v2(question: str, plan: Any, eligible_candidates: Any, payload_registry: Any, **kwargs: Any) -> dict[str, Any]:
        if len(contribution_calls) == 1:
            selected_ids = init_supp_ids
        else:
            selected_ids = tgt_supp_ids
        return {
            "policy_version": "v2",
            "selected_object_ids": selected_ids,
            "candidate_receipts": [],
            "selected_rank_keys": [],
        }
    monkeypatch.setattr("panda_agent.retrieval.select_structured_candidates_v2", fake_select_v2)

    agent = make_agent(tmp_path, vertex=vertex, retriever=retriever)
    out = agent._run_detailed(QUESTION, mode="runtime_e1_v2")
    trace = out["diagnostics"]["e3_trace"]
    assert trace["triggered"] is True

    # Call accounting invariants:
    # 2 channel collection calls: 1 initial retrieve, 1 targeted collection
    assert len(channel_calls) == 2
    # 2 structured contribution calls: 1 initial retrieve, 1 targeted collection
    assert len(contribution_calls) == 2

    # Rerank calls: exactly 1 in initial retrieve, 0 in targeted collection, exactly 1 in global rerank
    rerank_calls = [c for c in vertex.calls if c[0].get("task") == "rerank_evidence"]
    assert len(rerank_calls) == 2  # initial pass local rerank + E3 global rerank (targeted local rerank = 0)
    global_rerank_call = rerank_calls[1]

    # Global rerank query MUST be original question only
    assert global_rerank_call[0]["untrusted_question"] == QUESTION

    # Global rerank candidates payload
    rerank_cands = [c["object_id"] for c in global_rerank_call[0]["untrusted_candidates"]]
    # Saturated 30-item global pool: 24 base + 6 supplemental
    assert len(rerank_cands) == 30
    # Both initial 3 and targeted 3 supplemental candidates ALL reach the global reranker:
    for oid in init_supp_ids:
        assert oid in rerank_cands, f"initial supplemental candidate {oid} missing from global reranker"
    for oid in tgt_supp_ids:
        assert oid in rerank_cands, f"targeted supplemental candidate {oid} missing from global reranker"

    # Truthful provenance in pass_occurrences
    pass_occ = trace["pass_occurrences"]
    for oid in [*init_supp_ids, *tgt_supp_ids]:
        assert any(o["channel"] == "structured_replacement" and o["rank"] is None for o in pass_occ[oid])

    # Selector may reject: only selected evidence within final limit is kept
    final_eids = {e["object_id"] for e in out["diagnostics"]["selected_evidence"]}
    assert len(final_eids) <= 12
    assert not all(oid in final_eids for oid in [*init_supp_ids, *tgt_supp_ids])


def test_e3_real_retriever_preanswer_and_localbase_overlap_eligibility(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Correction 1 (Finding 2): Multi-pass consolidation preserves eligibility
    of structured candidate already in local base pool when it later drops global top-30,
    and includes pre-answer targeted supplemental candidate in global reranker."""
    init_base_items = [make_evidence(f"base_{i:02d}", channel="exact") for i in range(25)]
    overlap_item = make_evidence("overlap_s", channel="exact")
    init_base_items.append(overlap_item)  # rank 25 in initial base pool
    init_supp_ids = ["init_s1", "overlap_s"]

    pre_base_items = [make_evidence(f"pre_b_{i:02d}", channel="exact") for i in range(16)]
    pre_supp_ids = ["pre_s1"]

    tgt_base_items = [make_evidence(f"tgt_b_{i:02d}", channel="exact") for i in range(16)]
    tgt_supp_ids = ["tgt_s1"]

    vertex = FakeVertex(rerank_order=["overlap_s", "pre_s1", "init_s1", "tgt_s1"])
    retriever = Retriever.__new__(Retriever)
    retriever.vertex = vertex
    retriever.policies = SimpleNamespace(
        candidate_pool_per_channel=35,
        final_evidence_limit=12,
        max_relation_hops=2,
    )
    retriever._source_type = lambda payload: "code"
    retriever.analyze = lambda q, **kwargs: make_plan(symbols=["sym1"])
    retriever.query_expansions = SimpleNamespace(
        rules=[SimpleNamespace(rule_id="rule_sr", structured_replacement=True, triggers=["pndpidcorrelator", "what", "target", "objective"])]
    )
    retriever.storage = None
    retriever.context_sources = None

    plan = make_plan()

    # Pass 0: initial retrieve
    retriever._collect_channel_rankings = lambda q, p, lim: (
        {"exact": init_base_items, "dense": [], "sparse": [], "paper": [], "workflow": [], "graph": []},
        SimpleNamespace(text=q, intent="general", symbols=[], as_dict=lambda: {"intent": "general", "symbols": []}),
        [0.1, 0.2],
    )
    monkeypatch.setattr(
        "panda_agent.retrieval.build_structured_contribution_from_storage",
        lambda q, p, **kwargs: SimpleNamespace(
            bridged_payloads={oid: make_evidence(oid) for oid in init_supp_ids},
            bridge_receipts=[],
            reachability_receipts=[],
            resolution_receipt={},
            candidates=[],
        ),
    )
    monkeypatch.setattr(
        "panda_agent.retrieval.select_structured_candidates_v2",
        lambda q, p, ec, pr, **kwargs: {
            "policy_version": "v2",
            "selected_object_ids": init_supp_ids,
            "candidate_receipts": [],
            "selected_rank_keys": [],
        },
    )
    init_bundle = retriever.retrieve(QUESTION, plan=plan, capture_candidates=True)
    snap0 = init_bundle["candidate_snapshot"]
    assert "overlap_s" in [item["object_id"] for item in snap0["supplemental_candidates"]]

    # Pass 1: pre-answer targeted pass snapshot
    snap1 = {
        "pass_origin": "pre_answer_targeted_1",
        "rankings": {"exact": pre_base_items},
        "supplemental_candidates": [make_evidence(oid) for oid in pre_supp_ids],
    }

    # Pass 2: E3 targeted pass via real collect_channel_candidates
    retriever._collect_channel_rankings = lambda q, p, lim: (
        {"exact": tgt_base_items, "dense": [], "sparse": [], "paper": [], "workflow": [], "graph": []},
        SimpleNamespace(text=q, intent="general", symbols=[], as_dict=lambda: {"intent": "general", "symbols": []}),
        [0.1, 0.2],
    )
    monkeypatch.setattr(
        "panda_agent.retrieval.build_structured_contribution_from_storage",
        lambda q, p, **kwargs: SimpleNamespace(
            bridged_payloads={oid: make_evidence(oid) for oid in tgt_supp_ids},
            bridge_receipts=[],
            reachability_receipts=[],
            resolution_receipt={},
            candidates=[],
        ),
    )
    monkeypatch.setattr(
        "panda_agent.retrieval.select_structured_candidates_v2",
        lambda q, p, ec, pr, **kwargs: {
            "policy_version": "v2",
            "selected_object_ids": tgt_supp_ids,
            "candidate_receipts": [],
            "selected_rank_keys": [],
        },
    )
    tgt_coll = retriever.collect_channel_candidates("objective", plan)
    snap2 = {
        "pass_origin": "e3_targeted",
        "rankings": tgt_coll["rankings"],
        "supplemental_candidates": tgt_coll["supplemental_candidates"],
    }

    # Global consolidation across all 3 passes
    res = retriever.consolidate_and_select_candidates(
        original_question=QUESTION,
        plan=plan,
        pass_snapshots=[snap0, snap1, snap2],
    )
    assert res["status"] == "success"

    # Total base candidates: 26 + 16 + 16 = 58 candidates
    # Confirm overlap_s dropped out of the base top 30
    scores = res["scores"]
    base_fused = sorted([oid for oid in scores if res["best_channel_ranks"].get(oid)], key=lambda oid: (-scores[oid], oid))
    assert len(base_fused) > 30
    assert "overlap_s" not in base_fused[:30], "overlap_s should have dropped below top 30 base candidates"

    # Despite dropping out of top-30 base RRF, overlap_s was eligible supplemental and MUST reach global reranker:
    rerank_calls = [c for c in vertex.calls if c[0].get("task") == "rerank_evidence"]
    assert len(rerank_calls) == 2  # 1 in initial retrieve, 1 in global consolidate_and_select_candidates
    global_rerank_call = rerank_calls[1]
    rerank_cands = [c["object_id"] for c in global_rerank_call[0]["untrusted_candidates"]]
    assert len(rerank_cands) <= 30
    assert "overlap_s" in rerank_cands, "local base overlap structured candidate must be preserved in global rerank pool"
    assert "init_s1" in rerank_cands
    assert "pre_s1" in rerank_cands
    assert "tgt_s1" in rerank_cands


def test_sentinel_3_structured_capture_no_duplicate_helper_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Correction 1 (Section 18): Candidate capture incurs zero duplicate structured contribution/helper calls."""
    retriever = Retriever.__new__(Retriever)
    vertex = FakeVertex(rerank_order=["obj1"])
    retriever.vertex = vertex
    retriever.policies = SimpleNamespace(
        candidate_pool_per_channel=10,
        final_evidence_limit=12,
        max_relation_hops=2,
    )
    retriever._source_type = lambda payload: "code"
    retriever.analyze = lambda q, **kwargs: make_plan()
    retriever.query_expansions = SimpleNamespace(
        rules=[SimpleNamespace(rule_id="r1", structured_replacement=True)]
    )
    retriever.storage = None
    retriever.context_sources = None

    plan = make_plan()
    plan.analysis_diagnostics = {"matched_expansion_rules": ["r1"]}

    channel_calls: list[tuple[str, Any, int]] = []
    def fake_collect_channel_rankings(question: str, p: Any, limit: int) -> tuple[dict[str, list[dict[str, Any]]], Any, Any]:
        channel_calls.append((question, p, limit))
        ev = make_evidence("obj1", channel="exact")
        rankings = {"exact": [ev], "dense": [], "sparse": [], "paper": [], "workflow": [], "graph": []}
        semantic_query = SimpleNamespace(
            text="test question",
            intent="general",
            symbols=[],
            as_dict=lambda: {"intent": "general", "symbols": []},
        )
        return rankings, semantic_query, [0.1, 0.2]
    retriever._collect_channel_rankings = fake_collect_channel_rankings

    structured_contribution_calls: list[tuple[str, Any]] = []
    def spy_build_contribution(question: str, p: Any, **kwargs: Any) -> Any:
        structured_contribution_calls.append((question, p))
        return SimpleNamespace(
            bridged_payloads={"obj_struct": make_evidence("obj_struct")},
            bridge_receipts=[],
            reachability_receipts=[],
            resolution_receipt={},
            candidates=[],
        )
    monkeypatch.setattr("panda_agent.retrieval.build_structured_contribution_from_storage", spy_build_contribution)

    monkeypatch.setattr(
        "panda_agent.retrieval.select_structured_candidates_v2",
        lambda q, p, ec, pr, **kwargs: {
            "policy_version": "v2",
            "selected_object_ids": ["obj_struct"],
            "candidate_receipts": [],
            "selected_rank_keys": [],
        },
    )

    # Call 1: capture_candidates=False
    bundle_normal = retriever.retrieve("test question", plan=plan, capture_candidates=False)
    assert len(channel_calls) == 1
    assert len(structured_contribution_calls) == 1

    # Call 2: capture_candidates=True
    bundle_captured = retriever.retrieve("test question", plan=plan, capture_candidates=True)
    assert len(channel_calls) == 2  # Exactly 1 channel call per retrieve
    assert len(structured_contribution_calls) == 2  # Exactly 1 structured contribution call per retrieve: ZERO duplicate calls!

    # Truthful provenance: supplemental candidate captured in supplemental_candidates, not in rankings
    snapshot = bundle_captured["candidate_snapshot"]
    assert "obj_struct" not in [item["object_id"] for item in snapshot["rankings"].get("exact", [])]
    assert "obj_struct" in [item["object_id"] for item in snapshot.get("supplemental_candidates", [])]


def test_e3_second_verify_unchanged_retained_claim_satisfies_deterministic_requirement(tmp_path: Path) -> None:
    """Correction 2 (Section 19): Unchanged retained claim resolves displaced evidence and satisfies deterministic requirement."""
    agent = make_agent(tmp_path)
    e_old = {
        "evidence_id": stable_id("obj_old", "exact", prefix="evidence"),
        "object_id": "obj_old",
        "source_id": "luminosityfit",
        "source_version_id": "luminosityfit@18c09e91",
        "text": "PndLmdAcceptance stored via SetAcceptance member is used by generate1dmodel to apply acceptance factor.",
        "locator": {
            "path": "src/PndLmdFitFactory.cxx",
            "start_line": 10,
            "end_line": 30,
            "symbol": "PndLmdFitFactory::Create",
        },
        "retrieval_channels": ["exact"],
        "score": 1.0,
        "authority_level": "primary",
    }
    e_new = make_evidence("obj_new")

    claim_c = {
        "claim_id": "c1",
        "claim_text": "PndLmdAcceptance is stored via SetAcceptance and passed to generate1dmodel to apply the acceptance factor.",
        "evidence_ids": [e_old["evidence_id"]],
        "answer_point_ids": ["point.1"],
        "declared_answer_point_ids": ["point.1"],
    }

    state: dict[str, Any] = {
        "question": QUESTION,
        "bundle": {
            "evidence": [e_new],  # e_old is displaced from newly selected bundle
            "plan": {"resolved_versions": {"luminosityfit": "18c09e91"}},
        },
        "draft": {
            "claims": [deepcopy(claim_c)],
        },
        "retained_supported_claims": [
            deepcopy(claim_c),
        ],
        "retained_support_evidence": {
            e_old["evidence_id"]: e_old,
        },
        "answer_point_coverage_mode": "runtime_e1_v2",
        "runtime_answer_points": [{"answer_point_id": "point.1", "text": "Point 1"}],
        "answer_requirements": [
            {"id": "acceptance_factory_application", "text": "Acceptance factory application requirement."}
        ],
        "missing_point_retrieval_count": 1,
        "revision_count": 1,
    }

    v_out = agent._verify(state)
    # Claim c1 is valid via retained ledger
    assert not any("invalid evidence for c1" in err for err in v_out["errors"])
    # Deterministic requirement acceptance_factory_application is satisfied: no false missing requirement!
    assert "acceptance_factory_application" not in v_out.get("missing_requirement_ids", [])
    assert not any("acceptance_factory_application" in err for err in v_out["errors"])


def test_e3_second_verify_new_claim_cannot_satisfy_deterministic_requirement_via_ledger(tmp_path: Path) -> None:
    """Correction 2 (Section 20): New claim citing ledger-only evidence is marked invalid and cannot satisfy requirement."""
    agent = make_agent(tmp_path)
    e_old = {
        "evidence_id": stable_id("obj_old", "exact", prefix="evidence"),
        "object_id": "obj_old",
        "source_id": "luminosityfit",
        "source_version_id": "luminosityfit@18c09e91",
        "text": "PndLmdAcceptance stored via SetAcceptance member is used by generate1dmodel to apply acceptance factor.",
        "locator": {
            "path": "src/PndLmdFitFactory.cxx",
            "start_line": 10,
            "end_line": 30,
            "symbol": "PndLmdFitFactory::Create",
        },
        "retrieval_channels": ["exact"],
        "score": 1.0,
        "authority_level": "primary",
    }
    e_new = make_evidence("obj_new")

    # Round 1 had claim c1
    claim_c1 = {
        "claim_id": "c1",
        "claim_text": "Round 1 original text.",
        "evidence_ids": [e_old["evidence_id"]],
        "answer_point_ids": ["point.1"],
        "declared_answer_point_ids": ["point.1"],
    }

    # In round 2, a new claim c_new tries to cite e_old (displaced, ledger-only)
    claim_new = {
        "claim_id": "c_new",
        "claim_text": "PndLmdAcceptance is stored via SetAcceptance and passed to generate1dmodel to apply the acceptance factor.",
        "evidence_ids": [e_old["evidence_id"]],
        "answer_point_ids": ["point.1"],
        "declared_answer_point_ids": ["point.1"],
    }

    state: dict[str, Any] = {
        "question": QUESTION,
        "bundle": {
            "evidence": [e_new],  # e_old is NOT in bundle
            "plan": {"resolved_versions": {"luminosityfit": "18c09e91"}},
        },
        "draft": {
            "claims": [deepcopy(claim_new)],
        },
        "retained_supported_claims": [
            deepcopy(claim_c1),  # c_new is NOT in retained_supported_claims
        ],
        "retained_support_evidence": {
            e_old["evidence_id"]: e_old,
        },
        "answer_point_coverage_mode": "runtime_e1_v2",
        "runtime_answer_points": [{"answer_point_id": "point.1", "text": "Point 1"}],
        "answer_requirements": [
            {"id": "acceptance_factory_application", "text": "Acceptance factory application requirement."}
        ],
        "missing_point_retrieval_count": 1,
        "revision_count": 1,
    }

    v_out = agent._verify(state)
    # 1. Claim-level check marks c_new invalid
    assert any("invalid evidence for c_new" in err for err in v_out["errors"])
    # 2. c_new cannot satisfy deterministic requirement through ledger-only e_old!
    assert any("missing answer requirement acceptance_factory_application" in err for err in v_out["errors"])
    assert "acceptance_factory_application" in v_out.get("missing_requirement_ids", [])


def test_e3_second_verify_modified_claim_same_id_cannot_satisfy_deterministic_requirement_via_ledger(tmp_path: Path) -> None:
    """Correction 2 (Negative modifiedsameID): Claim keeping the same claim_id as retained claim
    but with modified text is recognized as modified, marked invalid, and cannot use ledger."""
    agent = make_agent(tmp_path)
    e_old = {
        "evidence_id": stable_id("obj_old", "exact", prefix="evidence"),
        "object_id": "obj_old",
        "source_id": "luminosityfit",
        "source_version_id": "luminosityfit@18c09e91",
        "text": "PndLmdAcceptance stored via SetAcceptance member is used by generate1dmodel to apply acceptance factor.",
        "locator": {
            "path": "src/PndLmdFitFactory.cxx",
            "start_line": 10,
            "end_line": 30,
            "symbol": "PndLmdFitFactory::Create",
        },
        "retrieval_channels": ["exact"],
        "score": 1.0,
        "authority_level": "primary",
    }
    e_new = make_evidence("obj_new")

    # Round 1 had claim c1
    claim_c1_original = {
        "claim_id": "c1",
        "claim_text": "Round 1 original text for claim c1.",
        "evidence_ids": [e_old["evidence_id"]],
        "answer_point_ids": ["point.1"],
        "declared_answer_point_ids": ["point.1"],
    }

    # In round 2, claim c1 keeps the same claim_id 'c1', but modifies its claim_text!
    claim_c1_modified = {
        "claim_id": "c1",
        "claim_text": "Modified text for claim c1 attempting to satisfy acceptance_factory_application.",
        "evidence_ids": [e_old["evidence_id"]],
        "answer_point_ids": ["point.1"],
        "declared_answer_point_ids": ["point.1"],
    }

    state: dict[str, Any] = {
        "question": QUESTION,
        "bundle": {
            "evidence": [e_new],  # e_old is NOT in bundle
            "plan": {"resolved_versions": {"luminosityfit": "18c09e91"}},
        },
        "draft": {
            "claims": [deepcopy(claim_c1_modified)],
        },
        "retained_supported_claims": [
            deepcopy(claim_c1_original),
        ],
        "retained_support_evidence": {
            e_old["evidence_id"]: e_old,
        },
        "answer_point_coverage_mode": "runtime_e1_v2",
        "runtime_answer_points": [{"answer_point_id": "point.1", "text": "Point 1"}],
        "answer_requirements": [
            {"id": "acceptance_factory_application", "text": "Acceptance factory application requirement."}
        ],
        "missing_point_retrieval_count": 1,
        "revision_count": 1,
    }

    v_out = agent._verify(state)
    # Claim-level verification MUST mark modified c1 invalid because e_old is displaced and claim text changed
    assert any("invalid evidence for c1" in err for err in v_out["errors"])
    # Modified c1 CANNOT satisfy requirement via displaced ledger evidence
    assert any("missing answer requirement acceptance_factory_application" in err for err in v_out["errors"])
    assert "acceptance_factory_application" in v_out.get("missing_requirement_ids", [])


def test_e3_second_verify_gate_not_active_when_not_e3_second_verify(tmp_path: Path) -> None:
    """Correction 2 (Gate invariant): Gate only opens on runtime E3 second verify (mode runtime_e1_v2,
    missing_point_retrieval_count 1, revision_count 1). Outside that, ledger evidence does not satisfy requirements."""
    agent = make_agent(tmp_path)
    e_old = {
        "evidence_id": stable_id("obj_old", "exact", prefix="evidence"),
        "object_id": "obj_old",
        "source_id": "luminosityfit",
        "source_version_id": "luminosityfit@18c09e91",
        "text": "PndLmdAcceptance stored via SetAcceptance member is used by generate1dmodel to apply acceptance factor.",
        "locator": {
            "path": "src/PndLmdFitFactory.cxx",
            "start_line": 10,
            "end_line": 30,
            "symbol": "PndLmdFitFactory::Create",
        },
        "retrieval_channels": ["exact"],
        "score": 1.0,
        "authority_level": "primary",
    }
    e_new = make_evidence("obj_new")

    claim_c = {
        "claim_id": "c1",
        "claim_text": "PndLmdAcceptance is stored via SetAcceptance and passed to generate1dmodel to apply the acceptance factor.",
        "evidence_ids": [e_old["evidence_id"]],
        "answer_point_ids": ["point.1"],
        "declared_answer_point_ids": ["point.1"],
    }

    base_state: dict[str, Any] = {
        "question": QUESTION,
        "bundle": {
            "evidence": [e_new],
            "plan": {"resolved_versions": {"luminosityfit": "18c09e91"}},
        },
        "draft": {
            "claims": [deepcopy(claim_c)],
        },
        "retained_supported_claims": [
            deepcopy(claim_c),
        ],
        "retained_support_evidence": {
            e_old["evidence_id"]: e_old,
        },
        "runtime_answer_points": [{"answer_point_id": "point.1", "text": "Point 1"}],
        "answer_requirements": [
            {"id": "acceptance_factory_application", "text": "Acceptance factory application requirement."}
        ],
    }

    # Case 1: mode is legacy_question_core (not runtime_e1_v2)
    s1 = dict(base_state, answer_point_coverage_mode="legacy_question_core", missing_point_retrieval_count=1, revision_count=1)
    v1 = agent._verify(s1)
    assert "acceptance_factory_application" in v1.get("missing_requirement_ids", [])

    # Case 2: missing_point_retrieval_count is 0 (initial verify, not second verify)
    s2 = dict(base_state, answer_point_coverage_mode="runtime_e1_v2", missing_point_retrieval_count=0, revision_count=1)
    v2 = agent._verify(s2)
    assert "acceptance_factory_application" in v2.get("missing_requirement_ids", [])

    # Case 3: revision_count is 0 (draft turn, not revised turn)
    s3 = dict(base_state, answer_point_coverage_mode="runtime_e1_v2", missing_point_retrieval_count=1, revision_count=0)
    v3 = agent._verify(s3)
    assert "acceptance_factory_application" in v3.get("missing_requirement_ids", [])
