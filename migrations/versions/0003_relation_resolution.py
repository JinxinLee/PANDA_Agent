"""Require real endpoints for accepted relations and retain unresolved candidates."""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    # Existing M2 relations used synthetic unresolved object IDs. They are reproducible
    # from normalized JSONL and must be removed before endpoint constraints are added.
    op.execute(
        """DELETE FROM relation_edges r
        WHERE NOT EXISTS (SELECT 1 FROM knowledge_objects k WHERE k.object_id=r.subject_id)
           OR NOT EXISTS (SELECT 1 FROM knowledge_objects k WHERE k.object_id=r.object_id)"""
    )
    op.execute(
        """CREATE TABLE IF NOT EXISTS relation_candidates (
        candidate_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, predicate TEXT NOT NULL,
        raw_target TEXT NOT NULL, resolution_status TEXT NOT NULL, payload JSONB NOT NULL)"""
    )
    op.execute("CREATE INDEX IF NOT EXISTS relation_candidate_subject_idx ON relation_candidates(subject_id,predicate)")
    op.execute("CREATE INDEX IF NOT EXISTS relation_candidate_status_idx ON relation_candidates(resolution_status)")
    op.execute(
        """DO $$ BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='relation_subject_fk') THEN
          ALTER TABLE relation_edges ADD CONSTRAINT relation_subject_fk
          FOREIGN KEY(subject_id) REFERENCES knowledge_objects(object_id) ON DELETE CASCADE;
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='relation_object_fk') THEN
          ALTER TABLE relation_edges ADD CONSTRAINT relation_object_fk
          FOREIGN KEY(object_id) REFERENCES knowledge_objects(object_id) ON DELETE CASCADE;
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='relation_candidate_subject_fk') THEN
          ALTER TABLE relation_candidates ADD CONSTRAINT relation_candidate_subject_fk
          FOREIGN KEY(subject_id) REFERENCES knowledge_objects(object_id) ON DELETE CASCADE;
        END IF;
        END $$"""
    )


def downgrade():
    op.execute("ALTER TABLE relation_candidates DROP CONSTRAINT IF EXISTS relation_candidate_subject_fk")
    op.execute("ALTER TABLE relation_edges DROP CONSTRAINT IF EXISTS relation_object_fk")
    op.execute("ALTER TABLE relation_edges DROP CONSTRAINT IF EXISTS relation_subject_fk")
    op.execute("DROP TABLE IF EXISTS relation_candidates")
