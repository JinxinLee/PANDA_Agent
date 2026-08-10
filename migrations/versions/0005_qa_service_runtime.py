"""P0 QA service runtime audit columns.

Revision ID: 0005
Revises: 0004
"""
from alembic import op


revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE qa_runs
      ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ,
      ADD COLUMN IF NOT EXISTS duration_ms INTEGER,
      ADD COLUMN IF NOT EXISTS intent TEXT,
      ADD COLUMN IF NOT EXISTS error_code TEXT,
      ADD COLUMN IF NOT EXISTS node_timings JSONB,
      ADD COLUMN IF NOT EXISTS model_usage JSONB;
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE qa_runs
      DROP COLUMN IF EXISTS model_usage,
      DROP COLUMN IF EXISTS node_timings,
      DROP COLUMN IF EXISTS error_code,
      DROP COLUMN IF EXISTS intent,
      DROP COLUMN IF EXISTS duration_ms,
      DROP COLUMN IF EXISTS completed_at;
    """)
