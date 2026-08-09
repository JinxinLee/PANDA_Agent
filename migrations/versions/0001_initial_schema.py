"""Initial PANDA QA storage schema."""
from alembic import op
from panda_agent.storage import SCHEMA_SQL

revision="0001"
down_revision=None
branch_labels=None
depends_on=None


def upgrade():
    op.execute(SCHEMA_SQL)


def downgrade():
    for table in ("qa_runs","embedding_records","ingestion_runs","workflow_steps","relation_candidates","relation_edges","knowledge_objects","source_versions"):
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
