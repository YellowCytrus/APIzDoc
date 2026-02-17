"""
Нормализованные ORM-модели стилей элементов.
Каждый тип элемента — отдельная таблица со связью 1:1 к Profile.
Имена колонок совпадают с полями Pydantic DTO для generic маппинга.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, Integer, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.sqlalchemy.profile import Profile


# ---------------------------------------------------------------------------
# bullet_list  →  #set list(...)
# ---------------------------------------------------------------------------
class BulletListStyle(Base):
    __tablename__ = "bullet_list_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    tight: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    marker: Mapped[list[str]] = mapped_column(
        ARRAY(String(64)), nullable=False, default=lambda: ["- ", "‣", "–"],
    )
    indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    body_indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    spacing: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")

    profile: Mapped[Profile] = relationship(back_populates="bullet_list_style")


# ---------------------------------------------------------------------------
# document  →  #set text(...)  +  #set par(leading: ...)
# ---------------------------------------------------------------------------
class DocumentStyle(Base):
    __tablename__ = "document_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    font_size: Mapped[float] = mapped_column(Float, nullable=False, default=12.0)
    line_spacing: Mapped[float] = mapped_column(Float, nullable=False, default=1.2)
    font: Mapped[str] = mapped_column(String(255), nullable=False, default="libertinus serif")
    weight: Mapped[str] = mapped_column(String(32), nullable=False, default="regular")
    style: Mapped[str] = mapped_column(String(32), nullable=False, default="normal")
    fill: Mapped[str] = mapped_column(String(64), nullable=False, default="black")
    lang: Mapped[str] = mapped_column(String(16), nullable=False, default="en")
    region: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, default=None)
    tracking: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    word_spacing: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    hyphenate: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=None)
    ligatures: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    number_type: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")
    number_width: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")

    profile: Mapped[Profile] = relationship(back_populates="document_style")


# ---------------------------------------------------------------------------
# figure  →  #set image(...)  +  #set figure(...)
# ---------------------------------------------------------------------------
class FigureStyle(Base):
    __tablename__ = "figure_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    width: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    height: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    placement: Mapped[str] = mapped_column(String(32), nullable=False, default="none")
    gap: Mapped[float] = mapped_column(Float, nullable=False, default=0.65)
    outlined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fit: Mapped[str] = mapped_column(String(32), nullable=False, default="cover")

    profile: Mapped[Profile] = relationship(back_populates="figure_style")


# ---------------------------------------------------------------------------
# footnote  →  #set footnote(...)  +  #set footnote.entry(...)
# ---------------------------------------------------------------------------
class FootnoteStyle(Base):
    __tablename__ = "footnote_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    marker_format: Mapped[str] = mapped_column(String(32), nullable=False, default="1")
    clearance: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    gap: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    indent: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    profile: Mapped[Profile] = relationship(back_populates="footnote_style")


# ---------------------------------------------------------------------------
# heading  →  #set heading(...)
# ---------------------------------------------------------------------------
class HeadingStyle(Base):
    __tablename__ = "heading_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    numbering: Mapped[str] = mapped_column(String(64), nullable=False, default="1.1.1")
    outlined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    bookmarked: Mapped[str] = mapped_column(String(16), nullable=False, default="auto")
    offset: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hanging_indent: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=None)

    profile: Mapped[Profile] = relationship(back_populates="heading_style")


# ---------------------------------------------------------------------------
# numbered_list  →  #set enum(...)
# ---------------------------------------------------------------------------
class NumberedListStyle(Base):
    __tablename__ = "numbered_list_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    tight: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    body_indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    spacing: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")
    numbering: Mapped[str] = mapped_column(String(64), nullable=False, default="1.")
    start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)
    full: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reversed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    number_align: Mapped[str] = mapped_column(String(32), nullable=False, default="end+top")

    profile: Mapped[Profile] = relationship(back_populates="numbered_list_style")


# ---------------------------------------------------------------------------
# par  →  #set par(...)
# ---------------------------------------------------------------------------
class ParStyle(Base):
    __tablename__ = "par_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    spacing: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    first_line_indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hanging_indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    justify: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    linebreaks: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")

    profile: Mapped[Profile] = relationship(back_populates="par_style")


# ---------------------------------------------------------------------------
# quote  →  #set quote(...)  + show/set pad
# ---------------------------------------------------------------------------
class QuoteStyle(Base):
    __tablename__ = "quote_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    indent: Mapped[float] = mapped_column(Float, nullable=False, default=1.5)
    block: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    quotes: Mapped[str] = mapped_column(String(16), nullable=False, default="auto")

    profile: Mapped[Profile] = relationship(back_populates="quote_style")


# ---------------------------------------------------------------------------
# table  →  #set table(...)
# ---------------------------------------------------------------------------
class TableStyle(Base):
    __tablename__ = "table_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    stroke: Mapped[str] = mapped_column(String(32), nullable=False, default="0.5pt")
    align: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")
    inset: Mapped[str] = mapped_column(String(32), nullable=False, default="5pt")
    fill: Mapped[str] = mapped_column(String(64), nullable=False, default="none")

    profile: Mapped[Profile] = relationship(back_populates="table_style")


# ===========================  NEW ELEMENTS  ================================

# ---------------------------------------------------------------------------
# page  →  #set page(...)
# ---------------------------------------------------------------------------
class PageStyle(Base):
    __tablename__ = "page_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    paper: Mapped[str] = mapped_column(String(64), nullable=False, default="a4")
    flipped: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    margin_top: Mapped[float] = mapped_column(Float, nullable=False, default=2.5)
    margin_bottom: Mapped[float] = mapped_column(Float, nullable=False, default=2.5)
    margin_left: Mapped[float] = mapped_column(Float, nullable=False, default=2.5)
    margin_right: Mapped[float] = mapped_column(Float, nullable=False, default=2.5)
    columns: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    numbering: Mapped[str] = mapped_column(String(64), nullable=False, default="none")
    number_align: Mapped[str] = mapped_column(String(32), nullable=False, default="center+bottom")

    profile: Mapped[Profile] = relationship(back_populates="page_style")


# ---------------------------------------------------------------------------
# raw  →  #set raw(...)
# ---------------------------------------------------------------------------
class RawStyle(Base):
    __tablename__ = "raw_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    tab_size: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    align: Mapped[str] = mapped_column(String(32), nullable=False, default="start")
    theme: Mapped[str] = mapped_column(String(64), nullable=False, default="auto")

    profile: Mapped[Profile] = relationship(back_populates="raw_style")


# ---------------------------------------------------------------------------
# strong  →  #set strong(...)
# ---------------------------------------------------------------------------
class StrongStyle(Base):
    __tablename__ = "strong_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    delta: Mapped[int] = mapped_column(Integer, nullable=False, default=300)

    profile: Mapped[Profile] = relationship(back_populates="strong_style")


# ---------------------------------------------------------------------------
# terms  →  #set terms(...)
# ---------------------------------------------------------------------------
class TermsStyle(Base):
    __tablename__ = "terms_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    tight: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hanging_indent: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    spacing: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")

    profile: Mapped[Profile] = relationship(back_populates="terms_style")


# ---------------------------------------------------------------------------
# outline  →  #set outline(...)
# ---------------------------------------------------------------------------
class OutlineStyle(Base):
    __tablename__ = "outline_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), unique=True, nullable=False,
    )
    depth: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)
    indent: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")

    profile: Mapped[Profile] = relationship(back_populates="outline_style")
