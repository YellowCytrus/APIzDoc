"""add heading_level_styles.numbering_enabled

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = inspect(conn)
    if "heading_level_styles" not in insp.get_table_names():
        return
    cols = [c["name"] for c in insp.get_columns("heading_level_styles")]
    if "numbering_enabled" not in cols:
        op.add_column(
            "heading_level_styles",
            sa.Column(
                "numbering_enabled",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("true"),
            ),
        )


def downgrade() -> None:
    conn = op.get_bind()
    insp = inspect(conn)
    if "heading_level_styles" not in insp.get_table_names():
        return
    cols = [c["name"] for c in insp.get_columns("heading_level_styles")]
    if "numbering_enabled" in cols:
        op.drop_column("heading_level_styles", "numbering_enabled")
