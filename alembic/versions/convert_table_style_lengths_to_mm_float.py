"""convert table stroke/inset to mm float

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-04-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, Sequence[str], None] = "e6f7a8b9c0d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_STROKE_MM = 0.1763888889
DEFAULT_INSET_MM = 1.7638888889


def _legacy_to_mm_expr(column_name: str, default_mm: float) -> str:
    return f"""
    CASE
      WHEN {column_name} ~ '^\\s*[0-9]+(\\.[0-9]+)?\\s*(mm)?\\s*$'
        THEN regexp_replace({column_name}, '[^0-9\\.]', '', 'g')::double precision
      WHEN {column_name} ~ '^\\s*[0-9]+(\\.[0-9]+)?\\s*cm\\s*$'
        THEN regexp_replace({column_name}, '[^0-9\\.]', '', 'g')::double precision * 10.0
      WHEN {column_name} ~ '^\\s*[0-9]+(\\.[0-9]+)?\\s*in\\s*$'
        THEN regexp_replace({column_name}, '[^0-9\\.]', '', 'g')::double precision * 25.4
      WHEN {column_name} ~ '^\\s*[0-9]+(\\.[0-9]+)?\\s*pt\\s*$'
        THEN regexp_replace({column_name}, '[^0-9\\.]', '', 'g')::double precision * (25.4 / 72.0)
      WHEN {column_name} ~ '^\\s*[0-9]+(\\.[0-9]+)?\\s*em\\s*$'
        THEN regexp_replace({column_name}, '[^0-9\\.]', '', 'g')::double precision * (12.0 * (25.4 / 72.0))
      WHEN {column_name} ~ '^\\s*[0-9]+(\\.[0-9]+)?\\s*$'
        THEN regexp_replace({column_name}, '[^0-9\\.]', '', 'g')::double precision
      ELSE {default_mm}
    END
    """


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "table_styles" not in insp.get_table_names():
        return

    stroke_type = next((c["type"] for c in insp.get_columns("table_styles") if c["name"] == "stroke"), None)
    inset_type = next((c["type"] for c in insp.get_columns("table_styles") if c["name"] == "inset"), None)
    if stroke_type is None or inset_type is None:
        return

    op.alter_column(
        "table_styles",
        "stroke",
        type_=sa.Float(),
        postgresql_using=_legacy_to_mm_expr("stroke", DEFAULT_STROKE_MM),
        existing_nullable=False,
    )
    op.alter_column(
        "table_styles",
        "inset",
        type_=sa.Float(),
        postgresql_using=_legacy_to_mm_expr("inset", DEFAULT_INSET_MM),
        existing_nullable=False,
    )


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "table_styles" not in insp.get_table_names():
        return

    op.alter_column(
        "table_styles",
        "stroke",
        type_=sa.String(length=32),
        postgresql_using="(stroke::text || 'mm')",
        existing_nullable=False,
    )
    op.alter_column(
        "table_styles",
        "inset",
        type_=sa.String(length=32),
        postgresql_using="(inset::text || 'mm')",
        existing_nullable=False,
    )
