from __future__ import annotations
import os
import unittest
from pathlib import Path

from psycopg.types.json import Jsonb
from qdrant_client import models

from panda_agent.indexing import apply_index
from panda_agent.storage import Storage


@unittest.skipUnless(os.getenv("RUN_RECONCILIATION_LIVE_TESTS")=="1","set RUN_RECONCILIATION_LIVE_TESTS=1")
class ReconciliationLiveTests(unittest.TestCase):
    def test_stale_sql_and_qdrant_records_are_deleted(self):
        root=Path(__file__).resolve().parents[2]; storage=Storage(); stale="test.stale.object"
        with storage.connect() as connection:
            connection.execute("""INSERT INTO knowledge_objects(object_id,object_type,source_id,source_version_id,title,text,authority_level,locator,metadata,canonical_locator,token_count,embedding_eligible,content_hash)
              VALUES(%s,'test','test','test@stale','stale','stale','derived',%s,%s,'stale',1,false,'stale') ON CONFLICT DO NOTHING""",(stale,Jsonb({}),Jsonb({})))
        storage.qdrant.upsert(collection_name=storage.settings.collection_name,points=[models.PointStruct(id=storage.point_id(stale),vector={"dense":[0.0]*3072,"sparse":models.SparseVector(indices=[1],values=[1.0])},payload={"object_id":stale,"source_id":"test","source_version_id":"test@stale","object_type":"test","authority_level":"derived"})],wait=True)
        result=apply_index(root)
        with storage.connect() as connection:
            self.assertEqual(connection.execute("select count(1) from knowledge_objects where object_id=%s",(stale,)).fetchone()[0],0)
        self.assertEqual(storage.qdrant.retrieve(collection_name=storage.settings.collection_name,ids=[storage.point_id(stale)]),[])
        self.assertGreaterEqual(result["deleted_sql_records"],1); self.assertGreaterEqual(result["deleted_vectors"],1)


if __name__=="__main__": unittest.main()
