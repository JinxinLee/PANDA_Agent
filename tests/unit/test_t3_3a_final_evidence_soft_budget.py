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
        selected, excluded, soft = select_final_evidence(
            ordered, payloads, scores, channels, plan, limit, mandatory or set()
        )
        return [ev.object_id for ev in selected], excluded, soft

    def test_duplicate_locator_remains_hard(self) -> None:
        ordered = ["a", "b"]
        payloads = {
            "a": _payload("a", "src", "same/path"),
            "b": _payload("b", "src", "same/path"),
        }
        selected, excluded, _ = self._select(ordered, payloads, _plan())
        self.assertIn("a", selected)
        self.assertNotIn("b", selected)
        self.assertTrue(any(e["reason"] == "duplicate_locator" for e in excluded))

    def test_normal_source_diversity_cap_still_works(self) -> None:
        # Five same-source candidates; only four fit under the hard cap.
        ordered = [f"c{i}" for i in range(5)]
        payloads = {oid: _payload(oid, "src", f"path/{i}") for i, oid in enumerate(ordered)}
        selected, _, _ = self._select(ordered, payloads, _plan())
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
        selected, excluded, _ = self._select(ordered, payloads, _plan(["code"]), limit=6)
        self.assertEqual(len(selected), 6)
        self.assertNotIn("c3", selected)

    def test_soft_budget_admits_high_ranked_required_distinct(self) -> None:
        # 6 non-required code candidates + 4 same-source required docs fill 10
        # slots; the 5th same-source required doc at rank 11 is admitted via the
        # one bounded source overflow.
        ordered = [f"code{i}" for i in range(6)] + [f"src{i}" for i in range(4)] + ["high"]
        payloads = {oid: _payload(oid, f"code{i}", f"code/{i}") for i, oid in enumerate(ordered[:6])}
        for i in range(4):
            payloads[f"src{i}"] = _payload(f"src{i}", "samesource", f"docs/src/{i}.html", documentation=True)
        payloads["high"] = _payload("high", "samesource", "docs/high.html", documentation=True)
        selected, excluded, soft = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertIn("high", selected)
        self.assertTrue(any(a["object_id"] == "high" for a in soft))
        self.assertFalse(any(e["object_id"] == "high" for e in excluded))

    def test_low_ranked_cannot_exploit_soft_budget(self) -> None:
        ordered = [f"low{i}" for i in range(12)] + ["late"]
        payloads = {oid: _payload(oid, "src", f"path/{i}") for i, oid in enumerate(ordered)}
        # "late" is rank 13 and would be blocked by source cap, but rank > limit so skipped.
        selected, excluded, _ = self._select(ordered, payloads, _plan(["documentation"]))
        self.assertNotIn("late", selected)
        self.assertTrue(any(e["object_id"] == "late" and e["reason"] == "source_diversity_cap" for e in excluded))

    def test_mandatory_symbol_bypasses_budget(self) -> None:
        ordered = [f"c{i}" for i in range(6)]
        payloads = {oid: _payload(oid, "src", f"path/{i}") for i, oid in enumerate(ordered)}
        # Make cap small by limit 3; mandatory candidate at rank 6 should still be included.
        selected, _, _ = self._select(ordered, payloads, _plan(["documentation"]), mandatory={"c5"}, limit=3)
        self.assertIn("c5", selected)

    def test_repeated_source_overflow_is_bounded(self) -> None:
        # With limit 12, source cap is 4. Four same-source docs fill the cap, a
        # fifth is admitted by the single source overflow, and a sixth is
        # rejected because the allowance is exhausted.
        ordered = ["a0", "a1", "a2", "a3", "b0", "a4", "a5"]
        payloads = {
            "a0": _payload("a0", "same", "docs/a0.html", documentation=True),
            "a1": _payload("a1", "same", "docs/a1.html", documentation=True),
            "a2": _payload("a2", "same", "docs/a2.html", documentation=True),
            "a3": _payload("a3", "same", "docs/a3.html", documentation=True),
            "b0": _payload("b0", "code0", "code/b0"),
            "a4": _payload("a4", "same", "docs/a4.html", documentation=True),
            "a5": _payload("a5", "same", "docs/a5.html", documentation=True),
        }
        selected, excluded, soft = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertIn("a4", selected)
        self.assertNotIn("a5", selected)
        self.assertTrue(any(e["object_id"] == "a5" and e["reason"] == "source_diversity_cap" for e in excluded))
        self.assertEqual(sum(1 for a in soft if a["object_id"] == "a4"), 1)

    def test_repeated_type_overflow_is_bounded(self) -> None:
        # With limit 6, code cap is 3. Three code candidates fill the cap, a
        # fourth is admitted by the single type overflow, and a fifth is rejected.
        ordered = ["c0", "c1", "c2", "d0", "c3", "c4"]
        payloads = {}
        for i in range(3):
            payloads[f"c{i}"] = _payload(f"c{i}", f"csrc{i}", f"code/{i}")
        payloads["d0"] = _payload("d0", "dsrc0", "docs/d0.html", documentation=True)
        payloads["c3"] = _payload("c3", "csrc3", "code/3")
        payloads["c4"] = _payload("c4", "csrc4", "code/4")
        selected, excluded, soft = self._select(ordered, payloads, _plan(["code"]), limit=6)
        self.assertIn("c3", selected)
        self.assertNotIn("c4", selected)
        self.assertTrue(any(e["object_id"] == "c4" and e["reason"] == "source_budget_cap" for e in excluded))
        self.assertEqual(sum(1 for a in soft if a["object_id"] == "c3"), 1)

    def test_both_cap_overflow_consumes_both_allowances(self) -> None:
        # With limit 6, source cap is 2 and code cap is 3. A same-source code
        # candidate after two same-source code candidates and one doc violates
        # both caps; it is admitted only by consuming both allowances.
        ordered = ["c0", "c1", "c2", "d0", "c3", "c4"]
        payloads = {
            "c0": _payload("c0", "same", "code/0"),
            "c1": _payload("c1", "other", "code/1"),
            "c2": _payload("c2", "same", "code/2"),
            "d0": _payload("d0", "dsrc0", "docs/d0.html", documentation=True),
            "c3": _payload("c3", "same", "code/3"),
            "c4": _payload("c4", "same", "code/4"),
        }
        selected, excluded, soft = self._select(ordered, payloads, _plan(["code"]), limit=6)
        self.assertIn("c3", selected)
        self.assertNotIn("c4", selected)
        admission = next(a for a in soft if a["object_id"] == "c3")
        self.assertTrue(admission["consumed_source_overflow"])
        self.assertTrue(admission["consumed_type_overflow"])
        self.assertTrue(any(e["object_id"] == "c4" and e["reason"] == "source_diversity_cap_and_source_budget_cap" for e in excluded))

    def test_non_required_type_cannot_overflow(self) -> None:
        ordered = ["c0", "c1", "c2", "c3"]
        payloads = {oid: _payload(oid, f"src{i}", f"code/{i}") for i, oid in enumerate(ordered)}
        # required_types is documentation, so code candidates cannot use soft
        # overflow even if they are high-ranked.
        selected, excluded, soft = self._select(ordered, payloads, _plan(["documentation"]), limit=6)
        self.assertNotIn("c3", selected)
        self.assertTrue(any(e["object_id"] == "c3" and e["reason"] == "source_budget_cap" for e in excluded))

    def test_total_evidence_limit_never_exceeded(self) -> None:
        ordered = [f"c{i}" for i in range(30)]
        payloads = {oid: _payload(oid, "src", f"path/{i}") for i, oid in enumerate(ordered)}
        selected, _, _ = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertLessEqual(len(selected), 12)


if __name__ == "__main__":
    unittest.main()
