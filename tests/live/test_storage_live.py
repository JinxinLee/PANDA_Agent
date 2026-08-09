from __future__ import annotations
import os
import unittest

from panda_agent.storage import Storage


@unittest.skipUnless(os.getenv("RUN_STORAGE_LIVE_TESTS")=="1","set RUN_STORAGE_LIVE_TESTS=1")
class StorageLiveTests(unittest.TestCase):
    def test_postgres_migration_and_qdrant_schema(self):
        storage=Storage(); storage.initialize()
        with storage.connect() as connection:
            self.assertEqual(connection.execute("select version_num from alembic_version").fetchone()[0],"0003")
            self.assertEqual(connection.execute("select count(1) from knowledge_objects").fetchone()[0],102868)
            self.assertEqual(connection.execute("select count(1) from relation_edges").fetchone()[0],64554)
            self.assertEqual(connection.execute("select count(1) from relation_candidates").fetchone()[0],372139)
        collection=storage.qdrant.get_collection(storage.settings.collection_name)
        self.assertEqual(collection.config.params.vectors["dense"].size,3072)
        self.assertIn("sparse",collection.config.params.sparse_vectors)
        self.assertEqual(set(collection.payload_schema),{"source_id","source_version_id","object_type","authority_level"})


if __name__=="__main__": unittest.main()
