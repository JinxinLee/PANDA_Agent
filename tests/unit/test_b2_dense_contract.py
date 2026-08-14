from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace
import unittest

from qdrant_client import models

from panda_agent.config import SPARSE_VECTOR_NAME
from panda_agent.indexing import (
    IndexIdentity,
    _compatible_cache_keys,
    _record_embedding_cache,
)
from panda_agent.sparse import SparseEncoderReceipt
from panda_agent.storage import Storage, StorageSettings


class _Result:
    def __init__(self, rows=(), row=None):
        self.rows = rows
        self.row = row

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.row


class _CacheConnection:
    def __init__(self, dimensions_by_key: dict[str, int]):
        self.dimensions_by_key = dimensions_by_key
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def execute(self, statement: str, params: tuple[object, ...]):
        self.calls.append((statement, params))
        if statement.startswith("SELECT cache_key"):
            keys, expected_dimensions = params
            return _Result(
                [(key,) for key in keys if self.dimensions_by_key.get(key) == expected_dimensions]
            )
        if statement.startswith("INSERT INTO embedding_records"):
            self.dimensions_by_key[str(params[0])] = int(params[5])
        return _Result()


class _StorageConnection:
    def execute(self, statement: str, *args):
        if "SELECT fingerprint" in statement:
            return _Result(row=None)
        return _Result()


class _Qdrant:
    def __init__(self, dense_size: int):
        self.collection = SimpleNamespace(
            config=SimpleNamespace(
                params=SimpleNamespace(
                    vectors={"dense": SimpleNamespace(size=dense_size)},
                    sparse_vectors={
                        SPARSE_VECTOR_NAME: models.SparseVectorParams(
                            modifier=models.Modifier.IDF
                        )
                    },
                )
            ),
            payload_schema={
                "source_id": {},
                "source_version_id": {},
                "object_type": {},
                "authority_level": {},
            },
        )

    def collection_exists(self, name: str) -> bool:
        return True

    def get_collection(self, name: str):
        return self.collection


def _identity(dimensions: int) -> IndexIdentity:
    return IndexIdentity(
        embedding_model="gemini-embedding-2",
        embedding_dimensions=dimensions,
        distance="cosine",
        sparse=_sparse_receipt(),
        index_schema_version="4",
    )


def _sparse_receipt() -> SparseEncoderReceipt:
    return SparseEncoderReceipt(
        model_name="Qdrant/bm25", language="english", vector_name="sparse", modifier="idf",
        k=1.2, b=0.75, avg_len=256, token_max_length=40, disable_stemmer=False,
        tokenizer="SimpleTokenizer", stemmer="SnowballStemmer", hash_function="mmh3.hash",
        fastembed_version="0.7.4", mmh3_version="5.2.1", py_rust_stemmers_version="0.1.8",
        stopwords_sha256="a" * 64,
    )


class DenseCacheContractTests(unittest.TestCase):
    def test_current_3072_receipt_is_reused(self) -> None:
        connection = _CacheConnection({"current": 3072})

        cached = _compatible_cache_keys(connection, ["current"], 3072)

        self.assertEqual(cached, {"current"})
        self.assertIn("dimensions=%s", connection.calls[0][0])
        self.assertEqual(connection.calls[0][1], (["current"], 3072))

    def test_wrong_dimension_receipt_is_not_reused_and_is_re_recorded(self) -> None:
        connection = _CacheConnection({"stale": 3072})

        self.assertEqual(_compatible_cache_keys(connection, ["stale"], 768), set())
        _record_embedding_cache(
            connection,
            cache_key="stale",
            object_id="object.current",
            model="gemini-embedding-2",
            task_type="RETRIEVAL_DOCUMENT",
            text_hash="text-hash",
            dimensions=768,
        )

        self.assertEqual(connection.dimensions_by_key["stale"], 768)
        statement, params = connection.calls[-1]
        self.assertIn("ON CONFLICT(cache_key) DO UPDATE", statement)
        self.assertIn("dimensions=excluded.dimensions", statement)
        self.assertEqual(params[-1], 768)

    def test_index_identity_fingerprint_distinguishes_dimensions(self) -> None:
        self.assertNotEqual(_identity(3072).fingerprint(), _identity(768).fingerprint())

    def test_existing_qdrant_dense_size_mismatch_remains_fail_closed(self) -> None:
        storage = Storage.__new__(Storage)
        storage.settings = StorageSettings(collection_name="b2-test")
        storage.qdrant = _Qdrant(dense_size=768)
        storage.connect = lambda: nullcontext(_StorageConnection())

        with self.assertRaisesRegex(RuntimeError, "Qdrant dense dimension mismatch"):
            storage.initialize(_identity(3072))


if __name__ == "__main__":
    unittest.main()
