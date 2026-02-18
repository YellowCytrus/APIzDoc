"""Style hierarchy restructure: text overrides, heading levels, equation, remove strong

Revision ID: 002
Revises: 001
Create Date: 2025-02-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    tables = set(insp.get_table_names())

    # 1. Create text_override_styles (if not exists)
    if "text_override_styles" not in tables:
        op.create_table(
            "text_override_styles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("font", sa.String(255), nullable=False, server_default="libertinus serif"),
            sa.Column("font_size", sa.Float(), nullable=False, server_default="12.0"),
            sa.Column("weight", sa.String(32), nullable=False, server_default="regular"),
            sa.Column("style", sa.String(32), nullable=False, server_default="normal"),
            sa.Column("fill", sa.String(64), nullable=False, server_default="black"),
            sa.Column("lang", sa.String(16), nullable=False, server_default="en"),
            sa.Column("region", sa.String(16), nullable=True),
            sa.Column("tracking", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("word_spacing", sa.Float(), nullable=False, server_default="100.0"),
            sa.Column("hyphenate", sa.Boolean(), nullable=True),
            sa.Column("ligatures", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("number_type", sa.String(32), nullable=False, server_default="auto"),
            sa.Column("number_width", sa.String(32), nullable=False, server_default="auto"),
            sa.PrimaryKeyConstraint("id"),
        )
        tables.add("text_override_styles")

    # 2. Create heading_level_styles (before altering heading_styles)
    if "heading_level_styles" not in tables:
        op.create_table(
            "heading_level_styles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("profile_id", sa.Integer(), nullable=False),
            sa.Column("level", sa.Integer(), nullable=False),
            sa.Column("outlined", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("bookmarked", sa.String(16), nullable=False, server_default="auto"),
            sa.Column("offset", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("text_override_style_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["text_override_style_id"], ["text_override_styles.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("profile_id", "level", name="uq_heading_level_profile_level"),
        )
        op.create_index("ix_heading_level_styles_profile_id", "heading_level_styles", ["profile_id"])
        tables.add("heading_level_styles")

    # 3. Migrate heading_styles data to heading_level_styles (create 6 levels per profile, if old cols exist)
    if "heading_styles" in tables:
        hs_cols = {c["name"] for c in insp.get_columns("heading_styles")}
        if "outlined" in hs_cols and "profile_id" in hs_cols:
            result = conn.execute(sa.text(
                "SELECT profile_id, outlined, bookmarked, offset FROM heading_styles"
            ))
            rows = result.fetchall()
            for row in rows:
                pid, outlined, bookmarked, offset = row
                for level in range(1, 7):
                    conn.execute(
                        sa.text("""
                            INSERT INTO heading_level_styles (profile_id, level, outlined, bookmarked, offset)
                            VALUES (:pid, :level, :outlined, :bookmarked, :offset)
                        """),
                        {"pid": pid, "level": level, "outlined": outlined, "bookmarked": bookmarked, "offset": offset},
                    )
            # 4. Alter heading_styles: drop outlined, bookmarked, offset, hanging_indent
            if "hanging_indent" in hs_cols:
                op.drop_column("heading_styles", "hanging_indent")
            if "offset" in hs_cols:
                op.drop_column("heading_styles", "offset")
            if "bookmarked" in hs_cols:
                op.drop_column("heading_styles", "bookmarked")
            if "outlined" in hs_cols:
                op.drop_column("heading_styles", "outlined")

    # 5. Add text_override_style_id to element tables
    for table in [
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
    ]:
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

    # 6. Create equation_styles
    if "equation_styles" not in tables:
        op.create_table(
            "equation_styles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("profile_id", sa.Integer(), nullable=False),
            sa.Column("text_override_style_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["text_override_style_id"], ["text_override_styles.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("profile_id", name="uq_equation_styles_profile_id"),
        )
        op.create_index("ix_equation_styles_profile_id", "equation_styles", ["profile_id"])

    # 7. Drop strong_styles
    if "strong_styles" in tables:
        op.drop_table("strong_styles")


def downgrade() -> None:
    # 7. Recreate strong_styles
    op.create_table(
        "strong_styles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False, server_default="300"),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", name="uq_strong_styles_profile_id"),
    )

    # 6. Drop equation_styles
    op.drop_index("ix_equation_styles_profile_id", table_name="equation_styles")
    op.drop_table("equation_styles")

    # 5. Remove text_override_style_id from element tables
    for table in [
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
    ]:
        op.drop_constraint(f"fk_{table}_text_override_style_id", table, type_="foreignkey")
        op.drop_column(table, "text_override_style_id")

    # 4. Restore heading_styles columns (use defaults)
    op.add_column("heading_styles", sa.Column("outlined", sa.Boolean(), nullable=False, server_default="true"))
    op.add_column("heading_styles", sa.Column("bookmarked", sa.String(16), nullable=False, server_default="auto"))
    op.add_column("heading_styles", sa.Column("offset", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("heading_styles", sa.Column("hanging_indent", sa.Float(), nullable=True))

    # Migrate first level back? Skip for downgrade - data loss acceptable

    # 2-3. Drop heading_level_styles
    op.drop_index("ix_heading_level_styles_profile_id", table_name="heading_level_styles")
    op.drop_table("heading_level_styles")

    # 1. Drop text_override_styles
    op.drop_table("text_override_styles")
