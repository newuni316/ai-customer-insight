"""添加 AI 决策结果表

Revision ID: 003
Revises: 002
Create Date: 2026-05-05
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "decisions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("user_type", sa.String(50)),
        sa.Column("churn_risk", sa.String(10)),
        sa.Column("recommended_action", sa.Text()),
        sa.Column("reasoning", sa.Text()),
        sa.Column("rule_based", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_decisions_user_id", "decisions", ["user_id"])
    op.create_index("ix_decisions_user_type", "decisions", ["user_type"])
    op.create_index("ix_decisions_churn_risk", "decisions", ["churn_risk"])


def downgrade() -> None:
    op.drop_index("ix_decisions_churn_risk")
    op.drop_index("ix_decisions_user_type")
    op.drop_index("ix_decisions_user_id")
    op.drop_table("decisions")
