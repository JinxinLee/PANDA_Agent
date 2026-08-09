"""Bound PostgreSQL FTS input while preserving complete object text."""
from alembic import op

revision="0002"
down_revision="0001"
branch_labels=None
depends_on=None


def upgrade():
    op.execute("DROP INDEX IF EXISTS knowledge_text_fts_idx")
    op.execute("CREATE INDEX knowledge_text_fts_idx ON knowledge_objects USING GIN(to_tsvector('english', left(title || ' ' || text, 250000)))")


def downgrade():
    op.execute("DROP INDEX IF EXISTS knowledge_text_fts_idx")
    op.execute("CREATE INDEX knowledge_text_fts_idx ON knowledge_objects USING GIN(to_tsvector('english', title || ' ' || text))")
