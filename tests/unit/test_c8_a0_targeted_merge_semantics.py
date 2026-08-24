"""C8-A0 focused static semantics tests for QA targeted-retrieval merge.

These tests pin the current production merge semantics in
``QAAgent._targeted_retrieve`` (src/panda_agent/qa.py) without executing the
QA graph, the retriever pipeline, Vertex, storage, or any external service.
They are inventory evidence for
``evaluation/baselines/manifests/phase_c_c8_a0_targeted_retrieval_boundary_inventory_v1.json``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from panda_agent.qa import QAAgent


class RecordingRetriever:
    """Return a fixed targeted bundle and record the targeted call inputs."""

    def __init__(self, targeted_bundle):
        self.targeted_bundle = targeted_bundle
        self.calls = []

    def retrieve(self, question, plan=None):
        self.calls.append({"question": question, "plan": plan})
        return self.targeted_bundle


class IdleVertex:
    def generate_json(self, *args, **kwargs):  # pragma: no cover - never called
        raise AssertionError("no model call may occur in these tests")


def evidence(evidence_id, *, score=1.0, text="evidence text"):
    return {
        "evidence_id": evidence_id,
        "object_id": f"o-{evidence_id}",
        "source_id": "pandaroot",
        "source_version_id": "pandaroot@18c09e91100db27867ded30e708b4dae95bd8357",
        "text": text,
        "locator": {"path": "pid/PndPidCorrelator.h", "start_line": 1, "end_line": 4},
        "retrieval_channels": ["exact"],
        "score": score,
        "authority_level": "primary",
    }


def plan_dict(symbols=None):
    return {
        "intent": "api",
        "routing_method": "rule",
        "target_repositories": ["pandaroot"],
        "resolved_versions": {
            "pandaroot": "18c09e91100db27867ded30e708b4dae95bd8357"
        },
        "version_conflicts": [],
        "concepts": [],
        "symbols": symbols or [],
        "concept_scopes": {},
        "source_budgets": {"code": 0.55, "documentation": 0.20, "readme": 0.10, "graph": 0.10, "paper": 0.05},
        "required_source_types": ["code"],
        "resolved_aliases": {},
        "premise_corrections": [],
        "paper_page_hints": {},
        "analysis_diagnostics": {},
    }


def initial_bundle(evidence_items, symbols=None):
    return {
        "plan": plan_dict(symbols),
        "rankings": {"exact": ["o-i1"]},
        "fusion_scores": {"o-i1": 0.5},
        "reranked_object_ids": ["o-i1"],
        "ranked_object_ids": ["o-i1"],
        "excluded": [{"object_id": "o-x", "reason": "source_budget_cap"}],
        "backfill_admissions": [],
        "evidence": evidence_items,
    }


def agent_for(targeted_bundle):
    retriever = RecordingRetriever(targeted_bundle)
    agent = QAAgent(Path.cwd(), retriever=retriever, vertex=IdleVertex())
    return agent, retriever


class TargetedMergeSemanticsTests(unittest.TestCase):
    def test_merge_order_is_targeted_first_then_initial(self):
        agent, retriever = agent_for(
            {"plan": plan_dict(), "evidence": [evidence("t1"), evidence("t2")]}
        )
        state = {
            "question": "Where is PndPidCorrelator?",
            "bundle": initial_bundle([evidence("i1")]),
            "errors": ["missing required source: code"],
            "retrieval_count": 0,
        }
        result = agent._targeted_retrieve(state)
        self.assertEqual(
            [item["evidence_id"] for item in result["bundle"]["evidence"]],
            ["t1", "t2", "i1"],
        )
        self.assertEqual(result["retrieval_count"], 1)

    def test_duplicate_collision_keeps_targeted_position_and_initial_payload(self):
        # Same evidence_id in both passes: the dict comprehension keeps the
        # FIRST (targeted) insertion position but stores the LAST-seen value,
        # so the initial-pass payload (including its score) survives in the
        # targeted slot.
        agent, _ = agent_for({"plan": plan_dict(), "evidence": [evidence("e1", score=9.5, text="targeted text")]})
        state = {
            "question": "Where is PndPidCorrelator?",
            "bundle": initial_bundle([evidence("e1", score=0.5, text="initial text")]),
            "errors": ["missing required source: code"],
            "retrieval_count": 0,
        }
        result = agent._targeted_retrieve(state)
        merged = result["bundle"]["evidence"]
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["evidence_id"], "e1")
        self.assertEqual(merged[0]["text"], "initial text")
        self.assertEqual(merged[0]["score"], 0.5)

    def test_merge_truncates_to_twelve_dropping_initial_tail_silently(self):
        targeted = [evidence(f"t{n:02d}") for n in range(1, 9)]
        initial = [evidence(f"i{n:02d}") for n in range(1, 9)]
        agent, _ = agent_for({"plan": plan_dict(), "evidence": targeted})
        state = {
            "question": "Where is PndPidCorrelator?",
            "bundle": initial_bundle(initial),
            "errors": ["missing required source: code"],
            "retrieval_count": 0,
        }
        result = agent._targeted_retrieve(state)
        merged_ids = [item["evidence_id"] for item in result["bundle"]["evidence"]]
        self.assertEqual(len(merged_ids), 12)
        self.assertEqual(merged_ids[:8], [f"t{n:02d}" for n in range(1, 9)])
        self.assertEqual(merged_ids[8:], ["i01", "i02", "i03", "i04"])

    def test_targeted_plan_prepends_error_symbols_without_mutating_bundle_plan(self):
        agent, retriever = agent_for({"plan": plan_dict(), "evidence": []})
        state = {
            "question": "Where is Foo::bar used?",
            "bundle": initial_bundle([evidence("i1")], symbols=["PndPidCorrelator"]),
            "errors": ["unsupported requested API symbol: Foo::bar"],
            "retrieval_count": 0,
        }
        result = agent._targeted_retrieve(state)
        targeted_plan = retriever.calls[0]["plan"]
        # Parsed from the error text after "symbol:" verbatim (no strip).
        self.assertEqual(targeted_plan.symbols, [" Foo::bar", "PndPidCorrelator"])
        # The original bundle plan is copied, not mutated in place.
        self.assertEqual(state["bundle"]["plan"]["symbols"], ["PndPidCorrelator"])
        # The returned bundle still carries the INITIAL plan.
        self.assertEqual(result["bundle"]["plan"]["symbols"], ["PndPidCorrelator"])

    def test_targeted_question_appends_required_sources_and_errors(self):
        agent, retriever = agent_for({"plan": plan_dict(), "evidence": []})
        state = {
            "question": "Where is PndPidCorrelator?",
            "bundle": initial_bundle([evidence("i1")]),
            "errors": ["missing required source: code"],
            "retrieval_count": 0,
        }
        agent._targeted_retrieve(state)
        self.assertEqual(
            retriever.calls[0]["question"],
            "Where is PndPidCorrelator?"
            "\nTarget missing evidence sources: code."
            " Missing evidence details: missing required source: code",
        )

    def test_bundle_shell_keeps_initial_metadata_and_discards_targeted_metadata(self):
        targeted_bundle = {
            "plan": plan_dict(symbols=["TARGETED-ONLY"]),
            "rankings": {"exact": ["o-t1"]},
            "fusion_scores": {"o-t1": 9.9},
            "evidence": [evidence("t1")],
        }
        agent, _ = agent_for(targeted_bundle)
        initial = initial_bundle([evidence("i1")])
        state = {
            "question": "Where is PndPidCorrelator?",
            "bundle": initial,
            "errors": ["missing required source: code"],
            "retrieval_count": 0,
        }
        result = agent._targeted_retrieve(state)
        bundle = result["bundle"]
        self.assertIs(bundle["rankings"], initial["rankings"])
        self.assertIs(bundle["fusion_scores"], initial["fusion_scores"])
        self.assertIs(bundle["excluded"], initial["excluded"])
        self.assertEqual(bundle["plan"]["symbols"], [])
        # Initial shell fields persist alongside the replaced evidence.
        self.assertIn("backfill_admissions", bundle)
        # Targeted metadata never enters the surviving bundle.
        self.assertNotIn("o-t1", bundle["rankings"]["exact"])


if __name__ == "__main__":
    unittest.main()
