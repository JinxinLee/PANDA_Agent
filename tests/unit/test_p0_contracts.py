from __future__ import annotations

import unittest


class P0ContractTests(unittest.TestCase):
    """Executable contracts added before the P0 implementation."""

    def test_sphinx_snapshot_hash_has_one_canonical_implementation(self) -> None:
        from panda_agent.source import compute_sphinx_snapshot_hash

        records = [
            {
                "url": "https://example.test/docs/index.html",
                "final_url": "https://example.test/docs/index.html",
                "status": 200,
                "content_type": "text/html; charset=utf-8",
                "sha256": "a" * 64,
            }
        ]
        first = compute_sphinx_snapshot_hash(records)
        second = compute_sphinx_snapshot_hash(list(reversed(records)))
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_relation_candidates_are_not_accepted_edges(self) -> None:
        from panda_agent.models import RelationCandidate

        value = RelationCandidate(
            candidate_id="candidate.1",
            subject_id="object.subject",
            predicate="CALLS",
            raw_target="PndTargetGenerator",
            source_version_ids=["pandaroot@sha"],
            resolution_scope="symbol",
            resolution_status="unresolved_internal",
            confidence=0.8,
        )
        self.assertEqual(value.resolution_status, "unresolved_internal")

    def test_answer_is_rendered_only_from_verified_claims(self) -> None:
        from panda_agent.models import ClaimCitation
        from panda_agent.qa import render_verified_answer

        claims = [
            ClaimCitation(
                claim_id="claim1",
                claim_text="PndTargetGenerator is present.",
                evidence_ids=["evidence.1"],
            )
        ]
        answer = render_verified_answer(claims)
        self.assertEqual(answer, "PndTargetGenerator is present. [evidence.1]")

    def test_qa_prompts_define_untrusted_data_boundary(self) -> None:
        from panda_agent.prompts import (
            ANSWER_SYSTEM_PROMPT,
            COMMON_SECURITY_SYSTEM_PROMPT,
            EVIDENCE_REVIEW_SYSTEM_PROMPT,
        )

        combined = " ".join(
            [COMMON_SECURITY_SYSTEM_PROMPT, ANSWER_SYSTEM_PROMPT, EVIDENCE_REVIEW_SYSTEM_PROMPT]
        ).lower()
        self.assertIn("untrusted", combined)
        self.assertIn("never follow", combined)


if __name__ == "__main__":
    unittest.main()
