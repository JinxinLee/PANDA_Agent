from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from panda_agent.evaluator_catalog import (
    EvaluatorCatalogError,
    catalog_fingerprint,
    catalog_receipt,
    load_evaluator_catalog,
    load_normalized_lookup,
    write_evaluator_catalog,
)
from panda_agent.evaluation_runner import load_object_lookup, run_evaluation


def _object(object_id: str, *, parent: str | None = None) -> dict[str, object]:
    return {
        "object_id": object_id,
        "object_type": "workflow-data-product-version" if parent is None else "function_chunk",
        "source_id": "curated_panda_domain",
        "source_version_id": "curated_panda_domain@1.0",
        "title": f"title {object_id}",
        "text": f"text {object_id}",
        "authority_level": "derived",
        "locator": {
            "path": "workflow/demo.yaml",
            "symbol": "PndDemo",
            "section_path": ["Workflow", "Demo"],
            "parent_object_id": parent,
        },
        "parent_object_id": parent,
        "chunk_parent_id": parent,
        "canonical_locator": f"workflow/demo.yaml:{object_id}",
        "token_count": 12,
        "embedding_eligible": True,
        "metadata": {
            "derived_from": parent,
            "workflow": {"data_product": "demo", "version": "1.0"},
        },
    }


class EvaluatorCatalogTests(unittest.TestCase):
    def _write_jsonl(self, path: Path, objects: list[dict[str, object]]) -> None:
        path.write_text(
            "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in objects),
            encoding="utf-8",
        )

    def test_deterministic_full_projection_round_trip_preserves_lookup_parity(self) -> None:
        parent = _object("object.parent")
        child = _object("object.child", parent="object.parent")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "knowledge_objects.jsonl"
            catalog = root / "catalog.json"
            self._write_jsonl(source, [child, parent])
            source_lookup = load_normalized_lookup(source)
            receipt = write_evaluator_catalog(source, catalog)
            restored_lookup = load_evaluator_catalog(catalog)
            self.assertEqual(restored_lookup, source_lookup)
            self.assertEqual(receipt.count, 2)
            self.assertEqual(receipt.sha256, catalog_fingerprint(source_lookup))
            self.assertEqual(catalog_receipt(catalog), receipt)
            self.assertEqual(
                restored_lookup["object.child"]["metadata"], child["metadata"],
            )
            self.assertEqual(
                restored_lookup["object.child"]["locator"], child["locator"],
            )
            with patch("panda_agent.evaluation_runner.normalized_dir", side_effect=AssertionError("must use catalog")):
                self.assertEqual(
                    load_object_lookup(root, evaluator_catalog_path=catalog), source_lookup,
                )

    def test_equivalent_source_order_produces_identical_catalog_bytes(self) -> None:
        parent = _object("object.parent")
        child = _object("object.child", parent="object.parent")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = root / "first.jsonl", root / "second.jsonl"
            self._write_jsonl(first, [parent, child])
            self._write_jsonl(second, [child, parent])
            first_catalog, second_catalog = root / "first.json", root / "second.json"
            self.assertEqual(
                write_evaluator_catalog(first, first_catalog),
                write_evaluator_catalog(second, second_catalog),
            )
            self.assertEqual(first_catalog.read_bytes(), second_catalog.read_bytes())

    def test_normalized_lookup_streams_instead_of_reading_the_complete_jsonl(self) -> None:
        parent = _object("object.parent")
        with TemporaryDirectory() as directory:
            source = Path(directory) / "objects.jsonl"
            self._write_jsonl(source, [parent])
            with patch.object(Path, "read_text", side_effect=AssertionError("must stream source JSONL")):
                self.assertEqual(load_normalized_lookup(source), {"object.parent": parent})

    def test_loader_rejects_noncanonical_or_duplicate_catalog(self) -> None:
        parent = _object("object.parent")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source, catalog = root / "objects.jsonl", root / "catalog.json"
            self._write_jsonl(source, [parent])
            write_evaluator_catalog(source, catalog)
            catalog.write_text(catalog.read_text(encoding="utf-8").replace("{", "{\n", 1), encoding="utf-8")
            with self.assertRaisesRegex(EvaluatorCatalogError, "canonical"):
                load_evaluator_catalog(catalog)

    def test_resume_rejects_catalog_bytes_changed_at_the_same_path_before_engine_creation(self) -> None:
        parent = _object("object.parent")
        changed = _object("object.changed")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source, catalog = root / "objects.jsonl", root / "catalog.json"
            self._write_jsonl(source, [parent])
            expected_receipt = write_evaluator_catalog(source, catalog)
            run_dir = root / "data" / "evaluation" / "runs" / "resume-case"
            run_dir.mkdir(parents=True)
            (run_dir / "manifest.json").write_text(json.dumps({
                "run_started_at": "2026-08-10T00:00:00+00:00",
                "evaluator_catalog": {
                    "schema_version": expected_receipt.schema_version,
                    "lookup_contract": expected_receipt.lookup_contract,
                    "sha256": expected_receipt.sha256,
                    "count": expected_receipt.count,
                },
            }), encoding="utf-8")
            self._write_jsonl(source, [changed])
            write_evaluator_catalog(source, catalog)
            dataset = SimpleNamespace(questions=[SimpleNamespace(split="dev")])
            with (
                patch("panda_agent.evaluation_runner.load_gold_dataset", return_value=dataset),
                patch("panda_agent.evaluation_runner.build_evaluation_manifest", return_value={}),
                patch("panda_agent.evaluation_runner.Retriever", side_effect=AssertionError("must reject before engine")),
            ):
                with self.assertRaisesRegex(ValueError, "catalog receipt mismatch"):
                    run_evaluation(
                        root,
                        mode="retrieval",
                        split="dev",
                        run_id="resume-case",
                        allow_draft=True,
                        resume=True,
                        dataset_path=root / "gold.yaml",
                        evaluator_catalog_path=catalog,
                    )


if __name__ == "__main__":
    unittest.main()
