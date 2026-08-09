"""P1 aliases and immutable index identity.

Revision ID: 0004
Revises: 0003
"""
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_aliases (
      alias_id TEXT PRIMARY KEY, alias_text TEXT NOT NULL, normalized_alias TEXT NOT NULL,
      target_object_id TEXT NOT NULL REFERENCES knowledge_objects(object_id) ON DELETE CASCADE,
      source_version_id TEXT NOT NULL, review_status TEXT NOT NULL, payload JSONB NOT NULL
    );
    CREATE INDEX IF NOT EXISTS knowledge_alias_normalized_idx ON knowledge_aliases(normalized_alias);
    CREATE TABLE IF NOT EXISTS index_identities (
      collection_name TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, payload JSONB NOT NULL,
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS index_identities; DROP TABLE IF EXISTS knowledge_aliases;")
