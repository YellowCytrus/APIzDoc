"""Move justify from par_styles to document_styles (global text setting)

Revision ID: 003
Revises: 002
Create Date: 2025-02-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    # 1. Add justify to document_styles (if not exists)
    doc_cols = {c["name"] for c in insp.get_columns("document_styles")}
    if "justify" not in doc_cols:
        op.add_column(
            "document_styles",
            sa.Column("justify", sa.Boolean(), nullable=False, server_default="false"),
        )

    # 2. Migrate par_styles.justify -> document_styles.justify for same profile (if par has it)
    par_cols = {c["name"] for c in insp.get_columns("par_styles")}
    if "justify" in par_cols:
        op.execute(sa.text("""
            UPDATE document_styles d
            SET justify = p.justify
            FROM par_styles p
            WHERE d.profile_id = p.profile_id
        """))
        op.drop_column("par_styles", "justify")


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    par_cols = {c["name"] for c in insp.get_columns("par_styles")}
    doc_cols = {c["name"] for c in insp.get_columns("document_styles")}

    if "justify" in doc_cols:
        if "justify" not in par_cols:
            op.add_column(
                "par_styles",
                sa.Column("justify", sa.Boolean(), nullable=False, server_default="false"),
            )
        op.execute(sa.text("""
            UPDATE par_styles p
            SET justify = d.justify
            FROM document_styles d
            WHERE p.profile_id = d.profile_id
        """))
        op.drop_column("document_styles", "justify")
