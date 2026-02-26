"""add heading_level_styles.break_before

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = inspect(conn)
    if "heading_level_styles" in insp.get_table_names():
        cols = [c["name"] for c in insp.get_columns("heading_level_styles")]
        if "break_before" not in cols:
            op.add_column(
                "heading_level_styles",
                sa.Column("break_before", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            )


def downgrade() -> None:
    conn = op.get_bind()
    insp = inspect(conn)
    if "heading_level_styles" in insp.get_table_names():
        cols = [c["name"] for c in insp.get_columns("heading_level_styles")]
        if "break_before" in cols:
            op.drop_column("heading_level_styles", "break_before")
