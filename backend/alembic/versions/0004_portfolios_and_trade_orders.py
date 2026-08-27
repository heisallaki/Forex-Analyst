import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "portfolios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("base_currency", sa.String(length=10), nullable=False, server_default="USD"),
        sa.Column("initial_balance", sa.Float(), nullable=False),
        sa.Column("current_balance", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_portfolios_user_id", "portfolios", ["user_id"])

    op.add_column("trades", sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("trades", sa.Column("stop_loss", sa.Float(), nullable=True))
    op.add_column("trades", sa.Column("take_profit", sa.Float(), nullable=True))
    op.create_foreign_key(
        "fk_trades_portfolio_id", "trades", "portfolios", ["portfolio_id"], ["id"]
    )
    op.create_index("ix_trades_portfolio_id", "trades", ["portfolio_id"])


def downgrade() -> None:
    op.drop_index("ix_trades_portfolio_id", table_name="trades")
    op.drop_constraint("fk_trades_portfolio_id", "trades", type_="foreignkey")
    op.drop_column("trades", "take_profit")
    op.drop_column("trades", "stop_loss")
    op.drop_column("trades", "portfolio_id")
    op.drop_index("ix_portfolios_user_id", table_name="portfolios")
    op.drop_table("portfolios")
