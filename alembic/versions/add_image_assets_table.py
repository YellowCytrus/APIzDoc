"""add image_assets table

Revision ID: a1b2c3d4e5f6
Revises: d0f63a1fa726
Create Date: 2026-02-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "d0f63a1fa726"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    if "image_assets" in inspect(conn).get_table_names():
        return
    op.create_table(
        "image_assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("path", sa.String(512), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_image_assets_path"), "image_assets", ["path"], unique=True)


def downgrade() -> None:
    conn = op.get_bind()
    if "image_assets" not in inspect(conn).get_table_names():
        return
    op.drop_index(op.f("ix_image_assets_path"), table_name="image_assets")
    op.drop_table("image_assets")
