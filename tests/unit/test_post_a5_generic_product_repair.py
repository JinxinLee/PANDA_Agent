"""T0 deterministic tests for the post-A5 generic product repair.

Workstream A: bounded-revision recovery must not silently discard genuinely new
revised content merely because the generator reused an existing local claim ID,
while identical-unsupported restatement stays blocked and the revision bound
stays at one.

Workstream B: the semantic coverage reviewer must return an explicit per-point
record separating relevance from completeness, deterministically validated.

Workstream C: the generation and verification contracts must forbid corpus-wide
negative-existence claims inferred from a non-exhaustive evidence subset, while
deterministic exact-absence machinery stays authoritative.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from panda_agent.prompts import (
    ANSWER_SYSTEM_PROMPT,
    EVIDENCE_REVIEW_SYSTEM_PROMPT,
)
from panda_agent.qa import (
    DEFAULT_ANSWER_POINT_MODE,
    QAAgent,
    _validate_answer_point_review,
)
from test_qa import FakeRetriever, FakeVertex


def _evidence(evidence_id: str = "e1") -> dict:
    return {
        "evidence_id": evidence_id,
        "object_id": f"object-{evidence_id}",
        "source_id": "pandaroot",
        "source_version_id": "pandaroot@locked",
        "object_type": "source_file_chunk",
        "retrieval_channels": ["dense"],
        "locator": {"path": "macro/master/Readme.md", "symbol": None},
        "text": "Master run and Master Tasks provide default settings and operation modes.",
        "authority_level": "primary",
    }


def _revision_state() -> dict:
    supported = {
        "claim_id": "c1",
        "claim_text": "Source the configuration script to set up the terminal.",
        "evidence_ids": ["e1"],
        "answer_point_ids": ["point.1"],
    }
    unsupported = {
        "claim_id": "c2",
        "claim_text": "The master task orchestrates the event loop.",
        "evidence_ids": ["e1"],
        "answer_point_ids": ["point.2"],
    }
    return {
        "question": "How do I set up the terminal and run a simulation macro?",
        "answer_point_coverage_mode": DEFAULT_ANSWER_POINT_MODE,
        "runtime_answer_points": [
            {"answer_point_id": "point.1", "text": "How to set up the terminal"},
            {"answer_point_id": "point.2", "text": "How the master run task participates"},
        ],
        "bundle": {"plan": {}, "evidence": [_evidence()]},
        "draft": {"claims": [supported, unsupported]},
        "supported_claims": [supported],
        "unsupported_claim_ids": ["c2"],
        "missing_answer_point_ids": ["point.2"],
        "answer_requirements": [],
        "missing_requirement_ids": [],
        "errors": ["missing answer point point.2"],
        "revision_count": 0,
    }


class RevisionRecoveryVertex(FakeVertex):
    """Revision returns genuinely new content that reuses the supported ID."""

    def generate_json(self, prompt, schema, **kwargs):
        payload = json.loads(prompt)
        if payload.get("task") == "decompose_user_question":
            return FakeVertex().generate_json(prompt, schema, **kwargs)
        if "supported" in schema.get("properties", {}):
            result = FakeVertex().generate_json(prompt, schema, **kwargs)
            mappings = []
            for item in payload["untrusted_claims"]:
                point = "point.1" if "terminal" in item["claim_text"] else "point.2"
                mappings.append({"claim_id": item["claim_id"], "answer_point_ids": [point]})
            result["claim_answer_point_mappings"] = mappings
            result["missing_answer_point_ids"] = []
            return result
        # Bounded revision emits new master-task content reusing c1.
        return {
            "claims": [
                {
                    "claim_id": "c1",
                    "claim_text": "Master run and Master Tasks provide default settings and operation modes for the simulation lifecycle.",
                    "evidence_ids": ["e1"],
                    "answer_point_ids": ["point.2"],
                }
            ]
        }


class RevisionRecoveryTests(unittest.TestCase):
    """T0-A: the bounded revision path can recover a missing obligation."""

    def _revised_state(self):
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever({"plan": {}, "evidence": [_evidence()]}), vertex=RevisionRecoveryVertex())
        state = _revision_state()
        return agent._revise(state)

    def test_a3_new_content_survives_id_collision(self) -> None:
        state = self._revised_state()
        claims = state["draft"]["claims"]
        texts = {c["claim_text"] for c in claims}
        self.assertIn(
            "Master run and Master Tasks provide default settings and operation modes for the simulation lifecycle.",
            texts,
        )
        ids = [c["claim_id"] for c in claims]
        self.assertEqual(len(ids), len(set(ids)))

    def test_a1_revised_claim_is_reverified_not_autoaccepted(self) -> None:
        state = self._revised_state()
        # Recovery resets verification state so the merge is reverified.
        self.assertEqual(state["supported_claims"], [])
        self.assertEqual(state["unsupported_claim_ids"], [])

    def test_a5_revision_bound_counts_once(self) -> None:
        state = self._revised_state()
        self.assertEqual(state["revision_count"], 1)

    def test_a4_identical_unsupported_restatement_stays_blocked(self) -> None:
        agent = QAAgent(Path.cwd(), retriever=FakeRetriever({"plan": {}, "evidence": [_evidence()]}), vertex=FakeVertex())

        class RestatementVertex(FakeVertex):
            def generate_json(self, prompt, schema, **kwargs):
                payload = json.loads(prompt)
                if payload.get("task") == "decompose_user_question":
                    return FakeVertex().generate_json(prompt, schema, **kwargs)
                if "supported" in schema.get("properties", {}):
                    return FakeVertex().generate_json(prompt, schema, **kwargs)
                return {
                    "claims": [
                        {
                            "claim_id": "c2",
                            "claim_text": "The master task orchestrates the event loop.",
                            "evidence_ids": ["e1"],
                            "answer_point_ids": ["point.2"],
                        }
                    ]
                }

        agent.generation_vertex = RestatementVertex()
        state = agent._revise(_revision_state())
        texts = [c["claim_text"] for c in state["draft"]["claims"]]
        self.assertNotIn("The master task orchestrates the event loop.", texts)


class CoverageCompletenessValidatorTests(unittest.TestCase):
    """T0-B: per-point completeness records are deterministically validated."""

    def _review(self, coverage, missing=None, mappings=None):
        claims = [
            {"claim_id": "c1", "claim_text": "Stage B exists.", "evidence_ids": ["e1"], "answer_point_ids": ["p1"]},
        ]
        review = {
            "supported": True,
            "unsupported_claim_ids": [],
            "irrelevant_claim_ids": [],
            "missing_requirement_ids": [],
            "reason": "",
            "claim_answer_point_mappings": mappings
            or [{"claim_id": "c1", "answer_point_ids": ["p1", "p2"]}],
            "missing_answer_point_ids": missing if missing is not None else [],
            "answer_point_coverage": coverage,
        }
        return _validate_answer_point_review(review, claims, {"p1", "p2"}, set())

    def test_b1_relevant_but_incomplete_point_stays_missing(self) -> None:
        mappings = self._review(
            [
                {"answer_point_id": "p1", "supporting_claim_ids": ["c1"], "complete": True},
                {"answer_point_id": "p2", "supporting_claim_ids": ["c1"], "complete": False},
            ],
            missing=["p2"],
        )
        self.assertEqual(mappings, {"c1": ["p1", "p2"]})

    def test_b2_incomplete_point_not_listed_missing_is_invalid(self) -> None:
        with self.assertRaises(ValueError):
            self._review(
                [
                    {"answer_point_id": "p1", "supporting_claim_ids": ["c1"], "complete": True},
                    {"answer_point_id": "p2", "supporting_claim_ids": ["c1"], "complete": False},
                ],
                missing=[],
            )

    def test_b3_complete_point_without_support_is_invalid(self) -> None:
        with self.assertRaises(ValueError):
            self._review(
                [
                    {"answer_point_id": "p1", "supporting_claim_ids": ["c1"], "complete": True},
                    {"answer_point_id": "p2", "supporting_claim_ids": [], "complete": True},
                ],
                missing=[],
            )

    def test_b4_unsupported_claim_cannot_complete_point(self) -> None:
        with self.assertRaises(ValueError):
            self._review(
                [
                    {"answer_point_id": "p1", "supporting_claim_ids": ["c1"], "complete": True},
                    {"answer_point_id": "p2", "supporting_claim_ids": ["c1"], "complete": True},
                ],
                missing=[],
                mappings=[{"claim_id": "c1", "answer_point_ids": ["p1"]}],
            )

    def test_b5_reviewer_not_generator_authority(self) -> None:
        # A generator-declared mapping to a point does not make it complete:
        # only the reviewer's per-point complete record does, and it must cover
        # every runtime point exactly once.
        with self.assertRaises(ValueError):
            self._review(
                [
                    {"answer_point_id": "p1", "supporting_claim_ids": ["c1"], "complete": True},
                ],
                missing=[],
            )


class NegativeExistenceContractTests(unittest.TestCase):
    """T0-C: corpus-wide absence must not be inferred from a partial subset."""

    def test_c1_generation_contract_forbids_corpus_negative_inference(self) -> None:
        prompt = ANSWER_SYSTEM_PROMPT.casefold()
        self.assertIn("non-exhaustive", prompt)
        self.assertIn("absence", prompt)
        self.assertIn("locked corpus", prompt)

    def test_c2_scoped_uncertainty_is_the_sanctioned_form(self) -> None:
        prompt = ANSWER_SYSTEM_PROMPT.casefold()
        self.assertIn("does not establish", prompt)

    def test_c4_verification_contract_rejects_contradicted_negation(self) -> None:
        prompt = EVIDENCE_REVIEW_SYSTEM_PROMPT.casefold()
        self.assertIn("non-exhaustive", prompt)
        self.assertIn("absence", prompt)
        self.assertIn("evidence", prompt)


if __name__ == "__main__":
    unittest.main()
