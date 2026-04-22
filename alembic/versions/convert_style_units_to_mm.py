"""convert covered style units to mm

Revision ID: e6f7a8b9c0d1
Revises: d4e5f6a7b8c9
Create Date: 2026-04-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e6f7a8b9c0d1"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PT_TO_MM = 25.4 / 72.0
CM_TO_MM = 10.0


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "document_styles" not in insp.get_table_names():
        return

    # Snapshot legacy profiles before any conversion.
    conn.execute(
        sa.text(
            """
            CREATE TEMP TABLE legacy_profiles_tmp AS
            SELECT profile_id, font_size
            FROM document_styles
            WHERE line_spacing <= 3.0
            """
        )
    )

    # Only convert profiles that still look legacy (line_spacing in em range).
    conn.execute(
        sa.text(
            """
            UPDATE document_styles d
            SET line_spacing = d.line_spacing * (d.font_size * :pt_to_mm)
            FROM legacy_profiles_tmp lp
            WHERE d.profile_id = lp.profile_id
            """
        ),
        {"pt_to_mm": PT_TO_MM},
    )

    conn.execute(
        sa.text(
            """
            UPDATE page_styles p
            SET
              margin_top = p.margin_top * :cm_to_mm,
              margin_bottom = p.margin_bottom * :cm_to_mm,
              margin_left = p.margin_left * :cm_to_mm,
              margin_right = p.margin_right * :cm_to_mm
            FROM legacy_profiles_tmp lp
            WHERE p.profile_id = lp.profile_id
              AND p.margin_top <= 10.0
              AND p.margin_bottom <= 10.0
              AND p.margin_left <= 10.0
              AND p.margin_right <= 10.0
            """
        ),
        {"cm_to_mm": CM_TO_MM},
    )

    conn.execute(
        sa.text(
            """
            UPDATE par_styles p
            SET
              spacing = p.spacing * (lp.font_size * :pt_to_mm),
              first_line_indent = p.first_line_indent * (lp.font_size * :pt_to_mm),
              hanging_indent = p.hanging_indent * (lp.font_size * :pt_to_mm)
            FROM legacy_profiles_tmp lp
            WHERE p.profile_id = lp.profile_id
              AND p.spacing <= 10.0
              AND p.first_line_indent <= 10.0
              AND p.hanging_indent <= 10.0
            """
        ),
        {"pt_to_mm": PT_TO_MM},
    )

    conn.execute(
        sa.text(
            """
            UPDATE bullet_list_styles b
            SET
              indent = b.indent * :pt_to_mm,
              body_indent = b.body_indent * (lp.font_size * :pt_to_mm)
            FROM legacy_profiles_tmp lp
            WHERE b.profile_id = lp.profile_id
              AND b.indent <= 20.0
              AND b.body_indent <= 10.0
            """
        ),
        {"pt_to_mm": PT_TO_MM},
    )

    conn.execute(
        sa.text(
            """
            UPDATE numbered_list_styles n
            SET
              indent = n.indent * :pt_to_mm,
              body_indent = n.body_indent * (lp.font_size * :pt_to_mm)
            FROM legacy_profiles_tmp lp
            WHERE n.profile_id = lp.profile_id
              AND n.indent <= 20.0
              AND n.body_indent <= 10.0
            """
        ),
        {"pt_to_mm": PT_TO_MM},
    )

    conn.execute(
        sa.text(
            """
            UPDATE figure_styles f
            SET
              width = f.width * (lp.font_size * :pt_to_mm),
              height = f.height * (lp.font_size * :pt_to_mm),
              gap = f.gap * (lp.font_size * :pt_to_mm)
            FROM legacy_profiles_tmp lp
            WHERE f.profile_id = lp.profile_id
              AND f.width <= 10.0
              AND f.height <= 10.0
              AND f.gap <= 10.0
            """
        ),
        {"pt_to_mm": PT_TO_MM},
    )

    conn.execute(
        sa.text(
            """
            UPDATE footnote_styles f
            SET
              clearance = f.clearance * (lp.font_size * :pt_to_mm),
              gap = f.gap * (lp.font_size * :pt_to_mm),
              indent = f.indent * (lp.font_size * :pt_to_mm)
            FROM legacy_profiles_tmp lp
            WHERE f.profile_id = lp.profile_id
              AND f.clearance <= 10.0
              AND f.gap <= 10.0
              AND f.indent <= 10.0
            """
        ),
        {"pt_to_mm": PT_TO_MM},
    )

    conn.execute(
        sa.text(
            """
            UPDATE quote_styles q
            SET indent = q.indent * (lp.font_size * :pt_to_mm)
            FROM legacy_profiles_tmp lp
            WHERE q.profile_id = lp.profile_id
              AND q.indent <= 10.0
            """
        ),
        {"pt_to_mm": PT_TO_MM},
    )

    conn.execute(
        sa.text(
            """
            UPDATE terms_styles t
            SET
              indent = t.indent * :pt_to_mm,
              hanging_indent = t.hanging_indent * (lp.font_size * :pt_to_mm)
            FROM legacy_profiles_tmp lp
            WHERE t.profile_id = lp.profile_id
              AND t.indent <= 20.0
              AND t.hanging_indent <= 10.0
            """
        ),
        {"pt_to_mm": PT_TO_MM},
    )

    conn.execute(sa.text("DROP TABLE legacy_profiles_tmp"))


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if "document_styles" not in insp.get_table_names():
        return

    conn.execute(
        sa.text(
            """
            UPDATE document_styles
            SET line_spacing = line_spacing / (font_size * :pt_to_mm)
            WHERE line_spacing > 3.0
            """
        ),
        {"pt_to_mm": PT_TO_MM},
    )
