from __future__ import annotations

import hashlib
import unittest
import uuid

from panda_agent.indexing import plan_b5_reindex_impact_from_records


def _object(object_id: str, text: str, *, eligible: bool = True) -> dict[str, object]:
    return {
        "object_id": object_id, "object_type": "function", "title": object_id,
        "text": text, "token_count": 12 if eligible else 2,
        "embedding_eligible": eligible,
    }


def _before(item: dict[str, object], *, point: bool = True, receipt: bool = True) -> dict[str, object]:
    dense = f"{item['title']}\n{item['text']}".encode("utf-8")
    return {
        "object_id": item["object_id"],
        "effective_embedding_eligibility": item["embedding_eligible"],
        "embedding_input_sha256": hashlib.sha256(dense).hexdigest(),
        "text_sha256": hashlib.sha256(str(item["text"]).encode()).hexdigest(),
        "deterministic_point_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"panda-qa:{item['object_id']}")),
        "qdrant_point_exists": point,
        "embedding_receipt_exists": receipt,
    }


class B5ImpactPlanTests(unittest.TestCase):
    def test_unchanged_point_is_reused_without_receipt(self) -> None:
        item = _object("same", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([_before(item, receipt=False)], [item])
        self.assertEqual(result["categories"]["unchanged_eligible_reuse"], 1)
        self.assertEqual(result["vectors"]["dense_documents"], 0)
        self.assertEqual(result["vectors"]["receipt_missing_unchanged_reused"], 1)

    def test_changed_and_new_objects_are_selected_once(self) -> None:
        old = _object("changed", "one two three four five six seven eight nine ten eleven twelve")
        changed = _object("changed", "one two three four five six seven eight nine ten eleven updated")
        new = _object("new", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([_before(old)], [changed, new], batch_size=1)
        self.assertEqual(result["vectors"]["reembed_object_ids"], ["changed", "new"])
        self.assertEqual(result["vectors"]["batches"], 2)

    def test_eligibility_loss_marks_existing_point_stale(self) -> None:
        old = _object("lost", "one two three four five six seven eight nine ten eleven twelve")
        lost = _object("lost", "tiny", eligible=False)
        result = plan_b5_reindex_impact_from_records([_before(old)], [lost])
        self.assertEqual(result["categories"]["eligibility_lost_remove"], 1)
        self.assertEqual(result["categories"]["stale_live_points_remove"], 1)

    def test_duplicate_ids_are_rejected(self) -> None:
        item = _object("duplicate", "one two three four five six seven eight nine ten eleven twelve")
        with self.assertRaises(ValueError):
            plan_b5_reindex_impact_from_records([], [item, item])

    def test_new_object_is_an_sql_insert(self) -> None:
        item = _object("new", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([], [item])
        self.assertEqual(result["sql"]["insert_object_ids"], ["new"])

    def test_removed_object_is_an_sql_delete(self) -> None:
        item = _object("removed", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([_before(item)], [])
        self.assertEqual(result["sql"]["delete_object_ids"], ["removed"])

    def test_no_live_point_is_not_counted_as_reusable(self) -> None:
        item = _object("unwritten", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([_before(item, point=False)], [item])
        self.assertEqual(result["categories"]["changed_eligible_reembed"], 1)

    def test_sparse_and_dense_document_counts_match(self) -> None:
        item = _object("new", "one two three four five six seven eight nine ten eleven twelve")
        result = plan_b5_reindex_impact_from_records([], [item])
        self.assertEqual(result["vectors"]["dense_documents"], result["vectors"]["sparse_documents"])

    def test_planner_never_calls_a_model(self) -> None:
        result = plan_b5_reindex_impact_from_records([], [])
        self.assertEqual(result["model_calls"], 0)
