from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("refresh_tokens_user_id_fkey", "refresh_tokens", type_="foreignkey")
    op.create_foreign_key(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("portfolios_user_id_fkey", "portfolios", type_="foreignkey")
    op.create_foreign_key(
        "portfolios_user_id_fkey", "portfolios", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )

    op.drop_constraint("fk_trades_portfolio_id", "trades", type_="foreignkey")
    op.create_foreign_key(
        "fk_trades_portfolio_id",
        "trades",
        "portfolios",
        ["portfolio_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("trades_signal_id_fkey", "trades", type_="foreignkey")
    op.create_foreign_key(
        "trades_signal_id_fkey", "trades", "signals", ["signal_id"], ["id"], ondelete="SET NULL"
    )

    op.drop_constraint("signals_strategy_id_fkey", "signals", type_="foreignkey")
    op.create_foreign_key(
        "signals_strategy_id_fkey",
        "signals",
        "strategies",
        ["strategy_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.drop_constraint("fk_signals_user_id", "signals", type_="foreignkey")
    op.create_foreign_key(
        "fk_signals_user_id", "signals", "users", ["user_id"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    op.drop_constraint("fk_signals_user_id", "signals", type_="foreignkey")
    op.create_foreign_key("fk_signals_user_id", "signals", "users", ["user_id"], ["id"])

    op.drop_constraint("signals_strategy_id_fkey", "signals", type_="foreignkey")
    op.create_foreign_key(
        "signals_strategy_id_fkey", "signals", "strategies", ["strategy_id"], ["id"]
    )

    op.drop_constraint("trades_signal_id_fkey", "trades", type_="foreignkey")
    op.create_foreign_key("trades_signal_id_fkey", "trades", "signals", ["signal_id"], ["id"])

    op.drop_constraint("fk_trades_portfolio_id", "trades", type_="foreignkey")
    op.create_foreign_key(
        "fk_trades_portfolio_id", "trades", "portfolios", ["portfolio_id"], ["id"]
    )

    op.drop_constraint("portfolios_user_id_fkey", "portfolios", type_="foreignkey")
    op.create_foreign_key("portfolios_user_id_fkey", "portfolios", "users", ["user_id"], ["id"])

    op.drop_constraint("refresh_tokens_user_id_fkey", "refresh_tokens", type_="foreignkey")
    op.create_foreign_key(
        "refresh_tokens_user_id_fkey", "refresh_tokens", "users", ["user_id"], ["id"]
    )
