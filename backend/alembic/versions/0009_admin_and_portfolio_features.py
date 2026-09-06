import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "strategies", sa.Column("version", sa.Integer(), nullable=False, server_default="1")
    )

    op.add_column("signals", sa.Column("outcome", sa.String(length=20), nullable=True))
    op.add_column("signals", sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column(
        "portfolios", sa.Column("leverage", sa.Float(), nullable=False, server_default="1.0")
    )

    op.add_column("trades", sa.Column("trailing_stop_distance", sa.Float(), nullable=True))
    op.add_column("trades", sa.Column("margin_used", sa.Float(), nullable=True))
    op.add_column(
        "trades", sa.Column("realized_pnl", sa.Float(), nullable=False, server_default="0.0")
    )

    op.create_table(
        "system_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("min_confidence_threshold", sa.Float(), nullable=False, server_default="0.55"),
        sa.Column("min_reward_risk_ratio", sa.Float(), nullable=False, server_default="1.2"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("system_settings")
    op.drop_column("trades", "realized_pnl")
    op.drop_column("trades", "margin_used")
    op.drop_column("trades", "trailing_stop_distance")
    op.drop_column("portfolios", "leverage")
    op.drop_column("signals", "evaluated_at")
    op.drop_column("signals", "outcome")
    op.drop_column("strategies", "version")
