"""D1-A1 focused T0: governed parent_object_id persistence contract.

The knowledge_objects table has no parent_object_id column; structural
containment is persisted inside the JSONB metadata column (D1-A0R2 freeze).
These tests pin the exact serialized-payload contract at the boundary without
connecting to PostgreSQL or Qdrant.
"""

from __future__ import annotations

import unittest

from panda_agent.models import AuthorityLevel, KnowledgeObject, SourceLocator
from panda_agent.storage import object_persisted_metadata, restore_object_parent

BOOST_ROOT = "data_product.restgas.boost_root"
EVENT_POCA = "data_product.restgas.event_poca"


def _object_record(object_id: str, parent_object_id: str | None) -> dict:
    """KnowledgeObject-shaped record as reconstructed from a persisted payload."""
    obj = KnowledgeObject(
        object_id=object_id,
        object_type="data_product",
        source_id="curated_panda_domain",
        source_version_id="curated_panda_domain@seed",
        title=object_id,
        text=object_id,
        authority_level=AuthorityLevel.DERIVED,
        locator=SourceLocator(),
        parent_object_id=parent_object_id,
        canonical_locator=object_id,
        metadata={"curated_seed": True, "identity_role": "canonical"},
    )
    return obj.model_dump(mode="json")


def _persisted_record(record: dict) -> dict:
    """Persisted representation as reconstructable from SQL.

    The knowledge_objects row carries no parent_object_id column, so the
    persisted record drops the top-level model field and keeps the governed
    parent only inside the JSONB metadata, exactly as upsert_objects writes it.
    """
    persisted = {
        key: value for key, value in record.items() if key != "parent_object_id"
    }
    persisted["metadata"] = object_persisted_metadata(
        record["metadata"], record["parent_object_id"]
    )
    return persisted


class ObjectPersistedMetadataTests(unittest.TestCase):
    def test_sets_key_when_model_parent_is_set(self) -> None:
        merged = object_persisted_metadata({}, BOOST_ROOT)
        self.assertEqual(merged, {"parent_object_id": BOOST_ROOT})

    def test_preserves_unrelated_metadata_keys_untouched(self) -> None:
        merged = object_persisted_metadata(
            {"curated_seed": True, "identity_role": "canonical"}, BOOST_ROOT
        )
        self.assertEqual(
            merged,
            {
                "curated_seed": True,
                "identity_role": "canonical",
                "parent_object_id": BOOST_ROOT,
            },
        )

    def test_input_metadata_is_never_mutated(self) -> None:
        metadata = {"curated_seed": True, "identity_role": "canonical"}
        object_persisted_metadata(metadata, BOOST_ROOT)
        self.assertEqual(metadata, {"curated_seed": True, "identity_role": "canonical"})

    def test_model_parent_none_without_metadata_key_passes_through_unchanged(self) -> None:
        metadata = {"curated_seed": True, "identity_role": "canonical"}
        merged = object_persisted_metadata(metadata, None)
        self.assertEqual(merged, {"curated_seed": True, "identity_role": "canonical"})
        self.assertNotIn("parent_object_id", merged)
        self.assertEqual(metadata, {"curated_seed": True, "identity_role": "canonical"})

    def test_same_value_in_metadata_does_not_conflict(self) -> None:
        merged = object_persisted_metadata({"parent_object_id": BOOST_ROOT}, BOOST_ROOT)
        self.assertEqual(merged, {"parent_object_id": BOOST_ROOT})


class PersistedMetadataConflictTests(unittest.TestCase):
    def test_model_parent_set_with_differing_metadata_value_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            object_persisted_metadata({"parent_object_id": "object.other"}, BOOST_ROOT)

    def test_model_parent_set_with_none_metadata_value_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            object_persisted_metadata({"parent_object_id": None}, BOOST_ROOT)

    def test_model_parent_none_with_metadata_key_present_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            object_persisted_metadata({"parent_object_id": BOOST_ROOT}, None)

    def test_model_parent_none_with_none_metadata_value_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            object_persisted_metadata({"parent_object_id": None}, None)


class ParentPersistenceRoundTripTests(unittest.TestCase):
    def test_round_trip_is_lossless(self) -> None:
        record = _object_record("object.child", BOOST_ROOT)
        persisted = _persisted_record(record)
        restored = restore_object_parent(persisted)
        self.assertEqual(restored["parent_object_id"], BOOST_ROOT)
        self.assertEqual(restored["metadata"]["parent_object_id"], BOOST_ROOT)
        self.assertEqual(restored["metadata"]["curated_seed"], True)
        self.assertEqual(restored["metadata"]["identity_role"], "canonical")

    def test_event_poca_seed_containment_round_trip(self) -> None:
        record = _object_record(EVENT_POCA, BOOST_ROOT)
        restored = restore_object_parent(_persisted_record(record))
        self.assertEqual(record["object_id"], EVENT_POCA)
        self.assertEqual(restored["parent_object_id"], BOOST_ROOT)
        self.assertEqual(restored["metadata"]["parent_object_id"], BOOST_ROOT)

    def test_object_without_parent_restores_none(self) -> None:
        record = _object_record("object.standalone", None)
        restored = restore_object_parent(_persisted_record(record))
        self.assertIsNone(restored["parent_object_id"])
        self.assertNotIn("parent_object_id", restored["metadata"])

    def test_restore_does_not_mutate_the_persisted_record(self) -> None:
        persisted = _persisted_record(_object_record(EVENT_POCA, BOOST_ROOT))
        restore_object_parent(persisted)
        self.assertNotIn("parent_object_id", persisted)
        self.assertEqual(persisted["metadata"]["parent_object_id"], BOOST_ROOT)


if __name__ == "__main__":
    unittest.main()
