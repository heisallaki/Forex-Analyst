import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("signals", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("signals", sa.Column("hidden_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key("fk_signals_user_id", "signals", "users", ["user_id"], ["id"])
    op.create_index("ix_signals_user_id", "signals", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_signals_user_id", table_name="signals")
    op.drop_constraint("fk_signals_user_id", "signals", type_="foreignkey")
    op.drop_column("signals", "hidden_at")
    op.drop_column("signals", "user_id")
