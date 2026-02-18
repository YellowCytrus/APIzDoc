"""Ensure text_override_style_id exists in element tables (fix for stamped 002)

Revision ID: 004
Revises: 003
Create Date: 2025-02-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "004"
down_revision: Union[str, Sequence[str], None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ELEMENT_TABLES = [
    "bullet_list_styles",
    "figure_styles",
    "footnote_styles",
    "numbered_list_styles",
    "outline_styles",
    "par_styles",
    "quote_styles",
    "raw_styles",
    "table_styles",
    "terms_styles",
]


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    tables = set(insp.get_table_names())

    for table in ELEMENT_TABLES:
        if table in tables:
            cols = {c["name"] for c in insp.get_columns(table)}
            if "text_override_style_id" not in cols:
                op.add_column(table, sa.Column("text_override_style_id", sa.Integer(), nullable=True))
                op.create_foreign_key(
                    f"fk_{table}_text_override_style_id",
                    table,
                    "text_override_styles",
                    ["text_override_style_id"],
                    ["id"],
                    ondelete="SET NULL",
                )


def downgrade() -> None:
    # Cannot safely remove - other migrations may depend on it
    pass
