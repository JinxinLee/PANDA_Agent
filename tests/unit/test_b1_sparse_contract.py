from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace
import unittest

from qdrant_client import models

from panda_agent.config import SPARSE_VECTOR_NAME
from panda_agent.storage import Storage, StorageSettings


class _Result:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row


class _Connection:
    def __init__(self, identity_row=None):
        self.identity_row = identity_row
        self.statements = []

    def execute(self, statement, *args):
        self.statements.append(statement)
        if "SELECT fingerprint" in statement:
            return _Result(self.identity_row)
        return _Result()


class _Qdrant:
    def __init__(self, *, exists, sparse_vectors, dense_size=3072):
        self.exists = exists
        self.created = []
        self.payload_indexes = []
        self.collection = SimpleNamespace(
            config=SimpleNamespace(
                params=SimpleNamespace(
                    vectors={"dense": SimpleNamespace(size=dense_size)},
                    sparse_vectors=sparse_vectors,
                )
            ),
            payload_schema={
                "source_id": {},
                "source_version_id": {},
                "object_type": {},
                "authority_level": {},
            },
        )

    def collection_exists(self, name):
        return self.exists

    def create_collection(self, **kwargs):
        self.created.append(kwargs)

    def get_collection(self, name):
        return self.collection

    def create_payload_index(self, **kwargs):
        self.payload_indexes.append(kwargs)


def _storage(qdrant, identity_row=None):
    storage = Storage.__new__(Storage)
    storage.settings = StorageSettings(collection_name="b1-test")
    storage.qdrant = qdrant
    storage.connections = []

    def connect():
        connection = _Connection(identity_row)
        storage.connections.append(connection)
        return nullcontext(connection)

    storage.connect = connect
    return storage


class SparseContractTests(unittest.TestCase):
    def test_new_collection_uses_server_side_idf_modifier(self):
        qdrant = _Qdrant(
            exists=False,
            sparse_vectors={
                SPARSE_VECTOR_NAME: models.SparseVectorParams(modifier=models.Modifier.IDF)
            },
        )

        _storage(qdrant).initialize()

        create = qdrant.created[0]
        config = create["sparse_vectors_config"][SPARSE_VECTOR_NAME]
        self.assertEqual(config.modifier, models.Modifier.IDF)
        self.assertEqual(create["vectors_config"]["dense"].size, 3072)

    def test_existing_collection_with_idf_modifier_is_compatible(self):
        qdrant = _Qdrant(
            exists=True,
            sparse_vectors={
                SPARSE_VECTOR_NAME: models.SparseVectorParams(modifier=models.Modifier.IDF)
            },
        )

        _storage(qdrant).initialize()

        self.assertEqual(qdrant.created, [])

    def test_missing_or_wrong_sparse_modifier_fails_closed(self):
        for sparse_vectors in (
            {},
            {SPARSE_VECTOR_NAME: models.SparseVectorParams()},
            {SPARSE_VECTOR_NAME: SimpleNamespace(modifier="none")},
        ):
            with self.subTest(sparse_vectors=sparse_vectors):
                qdrant = _Qdrant(exists=True, sparse_vectors=sparse_vectors)
                with self.assertRaisesRegex(RuntimeError, "sparse modifier mismatch"):
                    _storage(qdrant).initialize()

    def test_existing_identity_mismatch_fails_before_collection_change(self):
        qdrant = _Qdrant(
            exists=False,
            sparse_vectors={
                SPARSE_VECTOR_NAME: models.SparseVectorParams(modifier=models.Modifier.IDF)
            },
        )
        identity = SimpleNamespace(
            embedding_dimensions=3072,
            sparse_vector_name=SPARSE_VECTOR_NAME,
            sparse_modifier="idf",
            fingerprint=lambda: "new",
            model_dump=lambda **kwargs: {},
        )

        with self.assertRaisesRegex(RuntimeError, "index identity mismatch"):
            _storage(qdrant, identity_row=("old",)).initialize(identity)

        self.assertEqual(qdrant.created, [])

    def test_identity_sparse_contract_mismatch_fails_before_persist_or_create(self):
        qdrant = _Qdrant(
            exists=False,
            sparse_vectors={
                SPARSE_VECTOR_NAME: models.SparseVectorParams(modifier=models.Modifier.IDF)
            },
        )
        identity = SimpleNamespace(
            embedding_dimensions=3072,
            sparse_vector_name=SPARSE_VECTOR_NAME,
            sparse_modifier="none",
            fingerprint=lambda: "bad",
            model_dump=lambda **kwargs: {},
        )
        storage = _storage(qdrant)

        with self.assertRaisesRegex(RuntimeError, "identity sparse contract mismatch"):
            storage.initialize(identity)

        self.assertEqual(qdrant.created, [])
        self.assertEqual(storage.connections, [])


if __name__ == "__main__":
    unittest.main()
