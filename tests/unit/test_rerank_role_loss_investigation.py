"""Deterministic tests for the retrieval/rerank role-loss investigation record
(Workstream D). The mechanism is recorded as DEFERRED; these tests pin the
investigated facts without implementing any repair."""
from __future__ import annotations

import json
import unittest
from pathlib import Path


class RerankRoleLossInvestigationTests(unittest.TestCase):
    def test_rerank_pool_is_a_bounded_prefix_of_fused_order(self) -> None:
        source = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "panda_agent"
            / "retrieval.py"
        ).read_text(encoding="utf-8")
        self.assertIn("rerank_pool = fused_order[:30]", source)

    def test_g011_role_loss_mechanism_recorded_as_deferred(self) -> None:
        recon = json.loads(
            (Path(__file__).resolve().parents[2] / "evaluation" / "post_a5_generic_product_repair.json")
            .read_text(encoding="utf-8")
        )
        deferred = recon["deferred_mechanisms"]
        self.assertEqual(
            deferred["rerank_role_preservation_repair"],
            "DEFERRED / NO_SAFE_GENERIC_REPAIR_ESTABLISHED",
        )
        self.assertIn("fused_order[:30]", deferred["mechanism"])


if __name__ == "__main__":
    unittest.main()
