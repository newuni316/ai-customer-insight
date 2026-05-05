"""添加订单和用户画像表

Revision ID: 002
Revises: 001
Create Date: 2026-05-05
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("product", sa.String(255)),
        sa.Column("status", sa.String(50), server_default="completed"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("total_spent", sa.Float(), server_default="0.0"),
        sa.Column("avg_order_value", sa.Float(), server_default="0.0"),
        sa.Column("purchase_frequency", sa.Float(), server_default="0.0"),
        sa.Column("last_active_days", sa.Integer(), server_default="0"),
        sa.Column("rfm_score", sa.String(3), server_default="111"),
        sa.Column("user_level", sa.String(20), server_default="Low Value"),
        sa.Column("churn_risk", sa.String(10), server_default="low"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("user_profiles")
    op.drop_table("orders")
