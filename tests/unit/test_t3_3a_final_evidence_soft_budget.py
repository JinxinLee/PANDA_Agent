from __future__ import annotations

import unittest
from types import SimpleNamespace

from panda_agent.retrieval import select_final_evidence


def _payload(
    object_id: str,
    source_id: str = "src",
    path: str | None = None,
    *,
    documentation: bool = False,
) -> dict:
    if documentation:
        source_id = f"sphinx_{source_id}"
        path = path or f"docs/{object_id}.html"
    return {
        "object_id": object_id,
        "source_id": source_id,
        "source_version_id": f"{source_id}@v1",
        "object_type": "source_file_chunk",
        "text": f"text {object_id}",
        "locator": {"path": path or f"path/{object_id}", "start_line": 1, "end_line": 1},
        "authority_level": "primary",
    }


def _plan(required_types: list[str] | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        source_budgets={"documentation": 0.5, "code": 0.5},
        required_source_types=required_types or ["documentation"],
    )


class T33AFinalEvidenceSoftBudgetTests(unittest.TestCase):
    def _select(
        self,
        ordered: list[str],
        payloads: dict,
        plan: SimpleNamespace,
        mandatory: set[str] | None = None,
        limit: int = 12,
    ):
        scores = {oid: 1.0 for oid in ordered}
        channels = {oid: ["dense"] for oid in ordered}
        selected, excluded = select_final_evidence(
            ordered, payloads, scores, channels, plan, limit, mandatory or set()
        )
        return [ev.object_id for ev in selected], excluded

    def test_duplicate_locator_remains_hard(self) -> None:
        ordered = ["a", "b"]
        payloads = {
            "a": _payload("a", "src", "same/path"),
            "b": _payload("b", "src", "same/path"),
        }
        selected, excluded = self._select(ordered, payloads, _plan())
        self.assertIn("a", selected)
        self.assertNotIn("b", selected)
        self.assertTrue(any(e["reason"] == "duplicate_locator" for e in excluded))

    def test_normal_source_diversity_cap_still_works(self) -> None:
        # Five same-source candidates; only four fit under the hard cap.
        ordered = [f"c{i}" for i in range(5)]
        payloads = {oid: _payload(oid, "src", f"path/{i}") for i, oid in enumerate(ordered)}
        selected, _ = self._select(ordered, payloads, _plan())
        self.assertEqual(len(selected), 4)

    def test_normal_type_budget_still_works_for_low_ranked(self) -> None:
        # Code cap is 3 with limit 6. The 4th code candidate at rank 7 is
        # outside the soft-budget window and remains blocked.
        ordered = ["c0", "c1", "c2", "d0", "d1", "d2", "c3"]
        payloads = {}
        for i in range(3):
            payloads[f"c{i}"] = _payload(f"c{i}", f"csrc{i}", f"code/{i}")
        for i in range(3):
            payloads[f"d{i}"] = _payload(f"d{i}", f"dsrc{i}", f"docs/{i}.html", documentation=True)
        payloads["c3"] = _payload("c3", "csrc3", "code/3")
        selected, excluded = self._select(ordered, payloads, _plan(["code"]), limit=6)
        self.assertEqual(len(selected), 6)
        self.assertNotIn("c3", selected)

    def test_soft_budget_admits_high_ranked_required_distinct(self) -> None:
        # 7 other docs + 4 same-source docs fill 11 slots; the 5th same-source
        # required doc at rank 12 is within the evidence window and is admitted.
        ordered = [f"low{i}" for i in range(7)] + [f"src{i}" for i in range(4)] + ["high", "low7"]
        payloads = {oid: _payload(oid, f"other{i}", f"docs/other/{i}.html", documentation=True) for i, oid in enumerate(ordered)}
        for i in range(4):
            payloads[f"src{i}"] = _payload(f"src{i}", f"src{i}", f"docs/src/{i}.html", documentation=True)
        payloads["high"] = _payload("high", "srchigh", "docs/high.html", documentation=True)
        # Ensure high is the 5th from source 'srchigh'? Actually only one from srchigh, so not blocked by source cap.
        # To trigger source cap, use same source for src0..src3 and high.
        for i in range(4):
            payloads[f"src{i}"] = _payload(f"src{i}", "samesource", f"docs/src/{i}.html", documentation=True)
        payloads["high"] = _payload("high", "samesource", "docs/high.html", documentation=True)
        selected, _ = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertIn("high", selected)
        self.assertEqual(len(selected), 12)

    def test_low_ranked_cannot_exploit_soft_budget(self) -> None:
        ordered = [f"low{i}" for i in range(12)] + ["late"]
        payloads = {oid: _payload(oid, "src", f"path/{i}") for i, oid in enumerate(ordered)}
        # "late" is rank 13 and would be blocked by source cap, but rank > limit so skipped.
        selected, excluded = self._select(ordered, payloads, _plan(["documentation"]))
        self.assertNotIn("late", selected)
        self.assertTrue(any(e["object_id"] == "late" and e["reason"] == "source_diversity_cap" for e in excluded))

    def test_mandatory_symbol_bypasses_budget(self) -> None:
        ordered = [f"c{i}" for i in range(6)]
        payloads = {oid: _payload(oid, "src", f"path/{i}") for i, oid in enumerate(ordered)}
        # Make cap small by limit 3; mandatory candidate at rank 6 should still be included.
        selected, _ = self._select(ordered, payloads, _plan(["documentation"]), mandatory={"c5"}, limit=3)
        self.assertIn("c5", selected)

    def test_total_evidence_limit_never_exceeded(self) -> None:
        ordered = [f"c{i}" for i in range(30)]
        payloads = {oid: _payload(oid, "src", f"path/{i}") for i, oid in enumerate(ordered)}
        selected, _ = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertLessEqual(len(selected), 12)


if __name__ == "__main__":
    unittest.main()
