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


class T33ATwoPassBackfillTests(unittest.TestCase):
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
        selected, excluded, backfill = select_final_evidence(
            ordered, payloads, scores, channels, plan, limit, mandatory or set()
        )
        return [ev.object_id for ev in selected], excluded, backfill

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

    def test_hard_pass_evidence_is_preserved(self) -> None:
        ordered = [f"c{i}" for i in range(6)] + [f"d{i}" for i in range(4)] + ["high"]
        payloads = {oid: _payload(oid, f"code{i}", f"code/{i}") for i, oid in enumerate(ordered[:6])}
        for i in range(4):
            payloads[f"d{i}"] = _payload(f"d{i}", f"docsrc{i}", f"docs/{i}.html", documentation=True)
        payloads["high"] = _payload("high", "docsrc9", "docs/high.html", documentation=True)
        # With limit 12, hard pass selects 6 code + 4 docs; any backfill only appends.
        selected, _, _ = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertGreaterEqual(len(selected), 10)
        for i in range(6):
            self.assertIn(f"c{i}", selected)
        for i in range(4):
            self.assertIn(f"d{i}", selected)

    def test_g011_like_source_backfill(self) -> None:
        # Same required documentation source reaches its hard cap; one extra
        # high-ranked distinct required doc is backfilled when capacity remains.
        ordered = [f"code{i}" for i in range(4)] + [f"d{i}" for i in range(4)] + ["high"]
        payloads = {oid: _payload(oid, f"code{i}", f"code/{i}") for i, oid in enumerate(ordered[:4])}
        for i in range(4):
            payloads[f"d{i}"] = _payload(f"d{i}", "samesource", f"docs/{i}.html", documentation=True)
        payloads["high"] = _payload("high", "samesource", "docs/high.html", documentation=True)
        selected, excluded, backfill = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertIn("high", selected)
        self.assertTrue(any(a["object_id"] == "high" for a in backfill))
        self.assertFalse(any(e["object_id"] == "high" for e in excluded))

    def test_g016_like_type_backfill(self) -> None:
        # Required code type reaches its hard cap; one extra high-ranked distinct
        # code candidate is backfilled when capacity remains.
        ordered = ["c0", "c1", "c2", "d0", "c3"]
        payloads = {
            "c0": _payload("c0", "csrc0", "code/0"),
            "c1": _payload("c1", "csrc1", "code/1"),
            "c2": _payload("c2", "csrc2", "code/2"),
            "d0": _payload("d0", "dsrc0", "docs/d0.html", documentation=True),
            "c3": _payload("c3", "csrc3", "code/3"),
        }
        selected, excluded, backfill = self._select(ordered, payloads, _plan(["code"]), limit=6)
        self.assertIn("c3", selected)
        self.assertTrue(any(a["object_id"] == "c3" for a in backfill))
        self.assertFalse(any(e["object_id"] == "c3" for e in excluded))

    def test_no_unused_capacity_means_no_backfill(self) -> None:
        ordered = [f"c{i}" for i in range(6)] + [f"d{i}" for i in range(4)] + ["high"]
        payloads = {oid: _payload(oid, f"code{i}", f"code/{i}") for i, oid in enumerate(ordered[:6])}
        for i in range(4):
            payloads[f"d{i}"] = _payload(f"d{i}", f"docsrc{i}", f"docs/{i}.html", documentation=True)
        payloads["high"] = _payload("high", "docsrc9", "docs/high.html", documentation=True)
        selected, _, backfill = self._select(ordered, payloads, _plan(["documentation"]), limit=10)
        self.assertEqual(len(selected), 10)
        self.assertEqual(backfill, [])

    def test_non_required_type_cannot_backfill(self) -> None:
        ordered = ["c0", "c1", "c2", "c3"]
        payloads = {oid: _payload(oid, f"src{i}", f"code/{i}") for i, oid in enumerate(ordered)}
        # required_types is documentation, so code candidates cannot backfill.
        selected, excluded, backfill = self._select(ordered, payloads, _plan(["documentation"]), limit=6)
        self.assertNotIn("c3", selected)
        self.assertTrue(any(e["object_id"] == "c3" for e in excluded))
        self.assertFalse(any(a["object_id"] == "c3" for a in backfill))

    def test_rank_window_blocks_backfill(self) -> None:
        ordered = [f"c{i}" for i in range(6)] + [f"d{i}" for i in range(4)] + ["late"]
        payloads = {oid: _payload(oid, f"code{i}", f"code/{i}") for i, oid in enumerate(ordered[:6])}
        for i in range(4):
            payloads[f"d{i}"] = _payload(f"d{i}", f"docsrc{i}", f"docs/{i}.html", documentation=True)
        payloads["late"] = _payload("late", "docsrc9", "docs/late.html", documentation=True)
        # limit 12, late is rank 11 within window; make it rank 13 by adding more.
        ordered = [f"c{i}" for i in range(6)] + [f"d{i}" for i in range(6)] + ["late"]
        payloads = {oid: _payload(oid, f"code{i}", f"code/{i}") for i, oid in enumerate(ordered[:6])}
        for i in range(6):
            payloads[f"d{i}"] = _payload(f"d{i}", f"docsrc{i}", f"docs/{i}.html", documentation=True)
        payloads["late"] = _payload("late", "docsrc9", "docs/late.html", documentation=True)
        selected, _, backfill = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertNotIn("late", selected)
        self.assertFalse(any(a["object_id"] == "late" for a in backfill))

    def test_multiple_backfills_limited_by_unused_capacity(self) -> None:
        # Hard pass selects 4 (3 code + 1 doc), limit 6, so at most 2 backfills.
        ordered = ["c0", "c1", "c2", "d0", "c3", "c4", "c5"]
        payloads = {
            "c0": _payload("c0", "csrc0", "code/0"),
            "c1": _payload("c1", "csrc1", "code/1"),
            "c2": _payload("c2", "csrc2", "code/2"),
            "d0": _payload("d0", "dsrc0", "docs/d0.html", documentation=True),
            "c3": _payload("c3", "csrc3", "code/3"),
            "c4": _payload("c4", "csrc4", "code/4"),
            "c5": _payload("c5", "csrc5", "code/5"),
        }
        selected, _, backfill = self._select(ordered, payloads, _plan(["code"]), limit=6)
        self.assertEqual(len(selected), 6)
        self.assertEqual(len(backfill), 2)

    def test_final_limit_never_exceeded(self) -> None:
        ordered = [f"c{i}" for i in range(30)]
        payloads = {oid: _payload(oid, f"src{i}", f"code/{i}") for i, oid in enumerate(ordered)}
        selected, _, _ = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertLessEqual(len(selected), 12)

    def test_diagnostic_consistency(self) -> None:
        ordered = [f"code{i}" for i in range(4)] + [f"d{i}" for i in range(4)] + ["high"]
        payloads = {oid: _payload(oid, f"code{i}", f"code/{i}") for i, oid in enumerate(ordered[:4])}
        for i in range(4):
            payloads[f"d{i}"] = _payload(f"d{i}", "samesource", f"docs/{i}.html", documentation=True)
        payloads["high"] = _payload("high", "samesource", "docs/high.html", documentation=True)
        selected, excluded, backfill = self._select(ordered, payloads, _plan(["documentation"]), limit=12)
        self.assertIn("high", selected)
        self.assertTrue(any(a["object_id"] == "high" for a in backfill))
        self.assertFalse(any(e["object_id"] == "high" for e in excluded))


if __name__ == "__main__":
    unittest.main()
