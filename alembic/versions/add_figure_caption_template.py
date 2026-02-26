"""add figure_styles.caption_template

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    # Add column only if missing (e.g. test DB created with create_all already has it)
    insp = inspect(conn)
    if "figure_styles" in insp.get_table_names():
        cols = [c["name"] for c in insp.get_columns("figure_styles")]
        if "caption_template" not in cols:
            op.add_column(
                "figure_styles",
                sa.Column("caption_template", sa.String(256), nullable=True),
            )


def downgrade() -> None:
    conn = op.get_bind()
    insp = inspect(conn)
    if "figure_styles" in insp.get_table_names():
        cols = [c["name"] for c in insp.get_columns("figure_styles")]
        if "caption_template" in cols:
            op.drop_column("figure_styles", "caption_template")
