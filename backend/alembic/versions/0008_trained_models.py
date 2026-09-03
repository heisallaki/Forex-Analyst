import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trained_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=30), nullable=False),
        sa.Column("model_blob", sa.LargeBinary(), nullable=False),
        sa.Column("model_metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_trained_models_model_name", "trained_models", ["model_name"])
    op.create_index("ix_trained_models_created_at", "trained_models", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_trained_models_created_at", table_name="trained_models")
    op.drop_index("ix_trained_models_model_name", table_name="trained_models")
    op.drop_table("trained_models")