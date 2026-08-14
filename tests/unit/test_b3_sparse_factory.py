from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import nullcontext
from types import SimpleNamespace
import hashlib
import json
import unittest
from unittest.mock import Mock, patch

from fastembed import SparseTextEmbedding
from panda_agent.config import FastEmbedSettings
from panda_agent.indexing import IndexIdentity, LegacyIndexIdentity, migrate_b3_sparse_identity
from panda_agent.sparse import (
    SparseContractError,
    SparseEncoderReceipt,
    create_sparse_encoder,
    sparse_receipt,
)
from panda_agent.storage import Storage


def _receipt(*, stopwords_sha256: str = "a" * 64) -> SparseEncoderReceipt:
    return SparseEncoderReceipt(
        model_name="Qdrant/bm25", language="english", vector_name="sparse", modifier="idf",
        k=1.2, b=0.75, avg_len=256, token_max_length=40, disable_stemmer=False,
        tokenizer="SimpleTokenizer", stemmer="SnowballStemmer", hash_function="mmh3.hash",
        fastembed_version="0.7.4", mmh3_version="5.2.1", py_rust_stemmers_version="0.1.8",
        stopwords_sha256=stopwords_sha256,
    )


class SparseFactoryTests(unittest.TestCase):
    def _settings(self, root: Path) -> FastEmbedSettings:
        (root / "english.txt").write_text("the\nand\n", encoding="utf-8")
        return FastEmbedSettings(model_path=root)

    def test_factory_is_local_only_and_receipt_contains_semantic_parameters(self) -> None:
        with TemporaryDirectory() as temporary:
            settings = self._settings(Path(temporary))
            with (
                patch("panda_agent.sparse.version", side_effect=lambda name: {"fastembed": "0.7.4", "mmh3": "5.2.1", "py-rust-stemmers": "0.1.8"}[name]),
                patch("panda_agent.sparse.SparseTextEmbedding") as embedding,
            ):
                _, receipt = create_sparse_encoder(Path(temporary), settings=settings)
        self.assertEqual(receipt, _receipt(stopwords_sha256=receipt.stopwords_sha256))
        self.assertEqual(receipt.tokenizer, "SimpleTokenizer")
        self.assertEqual(receipt.stemmer, "SnowballStemmer")
        self.assertEqual(receipt.hash_function, "mmh3.hash")
        self.assertTrue(embedding.call_args.kwargs["local_files_only"])
        self.assertEqual(embedding.call_args.kwargs["k"], 1.2)
        self.assertEqual(embedding.call_args.kwargs["token_max_length"], 40)

    def test_receipt_excludes_model_path_but_binds_english_stopwords(self) -> None:
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            first_settings = self._settings(Path(first))
            second_settings = self._settings(Path(second))
            with patch("panda_agent.sparse.version", return_value="test"):
                self.assertEqual(sparse_receipt(first_settings), sparse_receipt(second_settings))
                (Path(second) / "english.txt").write_text("changed\n", encoding="utf-8")
                self.assertNotEqual(sparse_receipt(first_settings), sparse_receipt(second_settings))

    def test_missing_stopwords_fails_before_factory_and_cannot_download(self) -> None:
        with TemporaryDirectory() as temporary:
            settings = FastEmbedSettings(model_path=Path(temporary))
            with patch("panda_agent.sparse.SparseTextEmbedding") as embedding:
                with self.assertRaisesRegex(SparseContractError, "stopword asset is missing"):
                    create_sparse_encoder(Path(temporary), settings=settings)
            embedding.assert_not_called()

    def test_index_fingerprint_changes_for_each_sparse_semantic_change(self) -> None:
        first = IndexIdentity(
            embedding_model="gemini-embedding-2", embedding_dimensions=3072, distance="cosine",
            sparse=_receipt(), index_schema_version="4",
        )
        for field, value in (
            ("model_name", "Qdrant/bm25-v2"), ("language", "german"),
            ("modifier", "none"), ("k", 2.0), ("avg_len", 256.5),
            ("fastembed_version", "0.7.5"), ("stopwords_sha256", "b" * 64),
        ):
            with self.subTest(field=field):
                changed = first.model_copy(update={"sparse": first.sparse.model_copy(update={field: value})})
                self.assertNotEqual(first.fingerprint(), changed.fingerprint())

    def test_representative_legacy_and_factory_contract_arguments_are_identical(self) -> None:
        strings = ["PndTask::Run", "config.yaml", "event_poca", "luminosity fit", "BM25 idf"]
        with TemporaryDirectory() as temporary:
            settings = self._settings(Path(temporary))
            with (
                patch("panda_agent.sparse.version", return_value="test"),
                patch("panda_agent.sparse.SparseTextEmbedding") as embedding,
            ):
                create_sparse_encoder(Path(temporary), settings=settings)
        kwargs = embedding.call_args.kwargs
        legacy = {
            "model_name": "Qdrant/bm25", "specific_model_path": str(settings.model_path),
            "local_files_only": True, "language": "english", "k": 1.2, "b": 0.75,
            "avg_len": 256, "token_max_length": 40, "disable_stemmer": False,
        }
        self.assertEqual(kwargs, legacy)
        self.assertEqual(len(strings), 5)

    def test_representative_legacy_and_factory_query_and_document_vectors_match(self) -> None:
        root = Path(__file__).resolve().parents[2]
        strings = ["PndTask::Run", "config.yaml", "event_poca", "luminosity fit", "BM25 idf"]
        factory, _ = create_sparse_encoder(root)
        legacy = SparseTextEmbedding(
            model_name="Qdrant/bm25",
            specific_model_path=str(root / "data" / "runtime" / "fastembed" / "bm25"),
            local_files_only=True,
            language="english",
        )
        for factory_vectors, legacy_vectors in (
            (factory.query_embed(strings), legacy.query_embed(strings)),
            (factory.embed(strings), legacy.embed(strings)),
        ):
            for actual, expected in zip(factory_vectors, legacy_vectors):
                self.assertEqual(actual.indices.tolist(), expected.indices.tolist())
                self.assertEqual(actual.values.tolist(), expected.values.tolist())

    def test_only_shared_module_constructs_sparse_text_embedding(self) -> None:
        root = Path(__file__).resolve().parents[2] / "src" / "panda_agent"
        for name in ("indexing.py", "retrieval.py", "sparse_evaluation.py", "kb_bundle.py"):
            with self.subTest(name=name):
                text = (root / name).read_text(encoding="utf-8")
                self.assertIn("create_sparse_encoder", text)
                self.assertNotIn("SparseTextEmbedding(", text)

    def test_indexing_default_path_uses_factory_receipt_for_written_sparse_vector(self) -> None:
        from panda_agent import indexing

        receipt = _receipt()
        identity = IndexIdentity(
            embedding_model="gemini-embedding-2", embedding_dimensions=3072, distance="cosine",
            sparse=receipt, index_schema_version="4",
        )
        vector = SimpleNamespace(
            indices=SimpleNamespace(tolist=lambda: [3]), values=SimpleNamespace(tolist=lambda: [0.25]),
        )
        encoder = SimpleNamespace(embed=lambda texts: iter([vector]))
        connection = SimpleNamespace(execute=lambda *_: SimpleNamespace(fetchall=lambda: [], fetchone=lambda: (1,)))
        storage = SimpleNamespace(
            settings=SimpleNamespace(collection_name="collection"),
            initialize=Mock(), connect=lambda: nullcontext(connection), point_id=lambda object_id: f"point:{object_id}",
            upsert_source_versions=Mock(), upsert_objects=Mock(), upsert_aliases=Mock(), prune_table=Mock(return_value=0), qdrant=SimpleNamespace(
                retrieve=lambda **_: [], upsert=Mock(),
            ),
        )
        objects = [{
            "object_id": "object-1", "title": "title", "text": "text", "embedding_eligible": True,
            "token_count": 10, "source_id": "source", "source_version_id": "source@v1",
            "object_type": "code", "authority_level": "primary", "locator": {},
        }]
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "data" / "manifests" / "source_manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("{}", encoding="utf-8")
            (root / "ingestion_report.json").write_text(
                '{"relation_count":0,"relation_candidate_count":0}', encoding="utf-8"
            )
            with (
                patch.object(indexing, "Storage", return_value=storage),
                patch.object(indexing, "VertexSettings") as vertex_settings,
                patch.object(indexing, "IndexIdentity") as identity_type,
                patch.object(indexing, "normalized_dir", return_value=root),
                patch.object(indexing, "load_jsonl", side_effect=[objects, [], []]),
                patch.object(indexing, "VertexAIClient", return_value=SimpleNamespace(embed_documents=lambda _: [[0.1]])),
                patch.object(indexing, "create_sparse_encoder", return_value=(encoder, receipt)) as factory,
            ):
                vertex_settings.from_env.return_value = SimpleNamespace(
                    embedding_model="gemini-embedding-2", embedding_dimensions=3072,
                )
                identity_type.from_settings.return_value = identity
                result = indexing._apply_index(root, limit=1, skip_sql_sync=True)
        self.assertEqual(result["indexed_vectors"], 1)
        storage.initialize.assert_called_once_with(identity)
        factory.assert_called_once_with(root)
        point = storage.qdrant.upsert.call_args.kwargs["points"][0]
        self.assertIn(receipt.vector_name, point.vector)

    def test_storage_rejects_persisted_or_qdrant_receipt_mismatch(self) -> None:
        receipt = _receipt()
        identity = IndexIdentity(
            embedding_model="gemini-embedding-2", embedding_dimensions=3072, distance="cosine",
            sparse=receipt, index_schema_version="4",
        )

        class Result:
            def __init__(self, row): self.row = row
            def fetchone(self): return self.row

        class Connection:
            def __init__(self, fingerprint, payload): self.fingerprint, self.payload = fingerprint, payload
            def execute(self, statement, *_):
                return Result((self.fingerprint, self.payload))

        def storage_for(payload, fingerprint=None, modifier="idf"):
            storage = Storage.__new__(Storage)
            storage.settings = SimpleNamespace(collection_name="collection")
            storage.connect = lambda: nullcontext(Connection(fingerprint or identity.fingerprint(), payload))
            storage.qdrant = SimpleNamespace(get_collection=lambda _: SimpleNamespace(
                config=SimpleNamespace(params=SimpleNamespace(
                    sparse_vectors={"sparse": SimpleNamespace(modifier=modifier)}, vectors={"dense": SimpleNamespace(size=3072)}
                ))
            ))
            return storage

        storage_for(identity.model_dump(mode="json")).require_sparse_receipt(receipt)
        bad_payload = identity.model_copy(update={"sparse": receipt.model_copy(update={"k": 2.0})}).model_dump(mode="json")
        with self.assertRaisesRegex(RuntimeError, "persisted sparse receipt"):
            storage_for(bad_payload).require_sparse_receipt(receipt)
        with self.assertRaisesRegex(RuntimeError, "Qdrant sparse modifier mismatch"):
            storage_for(identity.model_dump(mode="json"), modifier="none").require_sparse_receipt(receipt)
        with self.assertRaisesRegex(RuntimeError, "schema is invalid"):
            storage_for({"sparse": receipt.model_dump(mode="json")}).require_sparse_receipt(receipt)
        self_consistent_schema3 = identity.model_dump(mode="json") | {"index_schema_version": "3"}
        schema3_fingerprint = hashlib.sha256(
            json.dumps(self_consistent_schema3, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(RuntimeError, "schema is invalid"):
            storage_for(self_consistent_schema3, fingerprint=schema3_fingerprint).require_sparse_receipt(receipt)
        with self.assertRaisesRegex(RuntimeError, "persisted sparse receipt"):
            storage_for(identity.model_dump(mode="json"), fingerprint="corrupt").require_sparse_receipt(receipt)

    def test_sparse_vector_comparison_is_order_independent_but_rejects_duplicates_and_mismatch(self) -> None:
        from panda_agent.indexing import _assert_sparse_vector_equal

        expected = SimpleNamespace(indices=[3, 8], values=[0.25, 0.5])
        reordered = SimpleNamespace(indices=[8, 3], values=[0.5, 0.25])
        _assert_sparse_vector_equal(expected, reordered)
        with self.assertRaisesRegex(RuntimeError, "duplicate"):
            _assert_sparse_vector_equal(expected, SimpleNamespace(indices=[3, 3], values=[0.25, 0.25]))
        with self.assertRaisesRegex(RuntimeError, "float32"):
            _assert_sparse_vector_equal(expected, SimpleNamespace(indices=[8, 3], values=[0.5, 0.75]))

    def test_b3_metadata_migration_is_dry_by_default_and_validates_vectors(self) -> None:
        receipt = _receipt()
        identity = IndexIdentity(
            embedding_model="gemini-embedding-2", embedding_dimensions=3072, distance="cosine",
            sparse=receipt, index_schema_version="4",
        )
        legacy = LegacyIndexIdentity(
            embedding_model="gemini-embedding-2", embedding_dimensions=3072, distance="cosine",
            sparse_model="Qdrant/bm25", sparse_vector_name="sparse", sparse_modifier="idf", index_schema_version="3",
        )
        samples = [(f"point:no-cache" if index == 0 else f"point:{index}", f"title-{index}", f"text-{index}") for index in range(8)]

        class Result:
            def __init__(self, row=None, rows=()): self.row, self.rows = row, rows
            def fetchone(self): return self.row
            def fetchall(self): return self.rows

        class Connection:
            def __init__(self): self.updates = 0
            def execute(self, statement, *_):
                if statement.startswith("SELECT fingerprint"):
                    return Result((legacy.fingerprint(), legacy.model_dump(mode="json")))
                if statement.startswith("UPDATE"):
                    self.updates += 1
                    return Result((identity.fingerprint(),))
                raise AssertionError(statement)

        connection = Connection()
        vectors = [SimpleNamespace(indices=[index, index + 10], values=[float(index) + 0.25, float(index) + 0.5]) for index in range(8)]
        points = [
            SimpleNamespace(
                id=point_id, payload={"title": title, "text": text},
                vector={"sparse": SimpleNamespace(
                    indices=list(reversed(vector.indices)), values=list(reversed(vector.values)),
                )},
            )
            for (point_id, title, text), vector in zip(samples, vectors)
        ]
        storage = Storage.__new__(Storage)
        storage.settings = SimpleNamespace(collection_name="collection")
        storage.connect = lambda: nullcontext(connection)
        storage.qdrant = SimpleNamespace(
            get_collection=lambda _: SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(
                sparse_vectors={"sparse": SimpleNamespace(modifier="idf")}, vectors={"dense": SimpleNamespace(size=3072)}
            ))),
            scroll=lambda **_: (points, None),
        )
        model = SimpleNamespace(embed=Mock(side_effect=lambda texts: iter(vectors)))
        settings = SimpleNamespace(embedding_model="gemini-embedding-2", embedding_dimensions=3072)
        with (
            patch("panda_agent.indexing.Storage", return_value=storage),
            patch("panda_agent.indexing.VertexSettings.from_env", return_value=settings),
            patch("panda_agent.indexing.IndexIdentity.from_settings", return_value=identity),
            patch("panda_agent.indexing.create_sparse_encoder", return_value=(model, receipt)) as factory,
        ):
            report = migrate_b3_sparse_identity(Path("."), run=False)
            applied = migrate_b3_sparse_identity(Path("."), run=True)
        self.assertTrue(report["valid"])
        self.assertTrue(report["dry_run"])
        self.assertEqual(report["sample_point_ids"][0], "point:no-cache")
        self.assertIn("Qdrant points", report["sampling_rule"])
        self.assertEqual(report["vectors_changed"], 0)
        self.assertFalse(applied["dry_run"])
        self.assertTrue(applied["updated"])
        self.assertEqual(connection.updates, 1)
        self.assertEqual(factory.call_count, 2)
        self.assertEqual(model.embed.call_args.args[0][0], "title-0\ntext-0")


if __name__ == "__main__":
    unittest.main()
