"""
Нормализованные ORM-модели стилей элементов.
Каждый тип элемента — отдельная таблица со связью 1:1 к Profile.
Имена колонок совпадают с полями Pydantic DTO для generic маппинга.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.sqlalchemy.profile import Profile


# ---------------------------------------------------------------------------
# text_override_styles — переопределения текста для элементов (без line_spacing)
# ---------------------------------------------------------------------------
def _text_override_to_dict(to: Optional["TextOverrideStyle"]) -> Optional[dict]:
    """Convert TextOverrideStyle to dict for API response."""
    if to is None:
        return None
    return {
        "font": to.font,
        "font_size": to.font_size,
        "weight": to.weight,
        "style": to.style,
        "fill": to.fill,
        "lang": to.lang,
        "region": to.region,
        "tracking": to.tracking,
        "word_spacing": to.word_spacing,
        "hyphenate": to.hyphenate,
        "ligatures": to.ligatures,
        "number_type": to.number_type,
        "number_width": to.number_width,
    }


class TextOverrideMixin:
    """Mixin for style models that have text_override_style_id."""

    @property
    def text_override(self) -> Optional[dict]:
        """For API serialization: dict or None."""
        return _text_override_to_dict(getattr(self, "text_override_style", None))


class TextOverrideStyle(Base):
    __tablename__ = "text_override_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Note: no profile_id - referenced by element tables via text_override_style_id
    font: Mapped[str] = mapped_column(String(255), nullable=False, default="libertinus serif")
    font_size: Mapped[float] = mapped_column(Float, nullable=False, default=12.0)
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


# ---------------------------------------------------------------------------
# bullet_list  →  #set list(...)
# ---------------------------------------------------------------------------
class BulletListStyle(TextOverrideMixin, Base):
    __tablename__ = "bullet_list_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    tight: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    marker: Mapped[list[str]] = mapped_column(
        ARRAY(String(64)),
        nullable=False,
        default=lambda: ["- ", "‣", "–"],
    )
    indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    body_indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    spacing: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="bullet_list_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# document  →  #set text(...)  +  #set par(leading: ...)
# ---------------------------------------------------------------------------
class DocumentStyle(Base):
    __tablename__ = "document_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
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
    justify: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    profile: Mapped[Profile] = relationship(back_populates="document_style")


# ---------------------------------------------------------------------------
# figure  →  #set image(...)  +  #set figure(...)
# ---------------------------------------------------------------------------
class FigureStyle(TextOverrideMixin, Base):
    __tablename__ = "figure_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    width: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    height: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    placement: Mapped[str] = mapped_column(String(32), nullable=False, default="none")
    gap: Mapped[float] = mapped_column(Float, nullable=False, default=0.65)
    outlined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fit: Mapped[str] = mapped_column(String(32), nullable=False, default="cover")
    caption_template: Mapped[Optional[str]] = mapped_column(
        String(256), nullable=True, default=None
    )
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="figure_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# footnote  →  #set footnote(...)  +  #set footnote.entry(...)
# ---------------------------------------------------------------------------
class FootnoteStyle(TextOverrideMixin, Base):
    __tablename__ = "footnote_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    marker_format: Mapped[str] = mapped_column(String(32), nullable=False, default="1")
    clearance: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    gap: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    indent: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="footnote_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# heading  →  #set heading(...) — только numbering (глобально для всех уровней)
# ---------------------------------------------------------------------------
class HeadingStyle(Base):
    __tablename__ = "heading_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    numbering: Mapped[str] = mapped_column(String(64), nullable=False, default="1.1.1")

    profile: Mapped[Profile] = relationship(back_populates="heading_style")


# ---------------------------------------------------------------------------
# heading_level  →  per-level: outlined, bookmarked, offset + text override
# ---------------------------------------------------------------------------
class HeadingLevelStyle(TextOverrideMixin, Base):
    __tablename__ = "heading_level_styles"
    __table_args__ = (
        UniqueConstraint("profile_id", "level", name="uq_heading_level_profile_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–6
    outlined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    bookmarked: Mapped[str] = mapped_column(String(16), nullable=False, default="auto")
    offset: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="heading_level_styles")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# numbered_list  →  #set enum(...)
# ---------------------------------------------------------------------------
class NumberedListStyle(TextOverrideMixin, Base):
    __tablename__ = "numbered_list_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
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
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="numbered_list_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# par  →  #set par(...)
# ---------------------------------------------------------------------------
class ParStyle(TextOverrideMixin, Base):
    __tablename__ = "par_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    spacing: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    first_line_indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hanging_indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    linebreaks: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="par_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# quote  →  #set quote(...)  + show/set pad
# ---------------------------------------------------------------------------
class QuoteStyle(TextOverrideMixin, Base):
    __tablename__ = "quote_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    indent: Mapped[float] = mapped_column(Float, nullable=False, default=1.5)
    block: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    quotes: Mapped[str] = mapped_column(String(16), nullable=False, default="auto")
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="quote_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# table  →  #set table(...)
# ---------------------------------------------------------------------------
class TableStyle(TextOverrideMixin, Base):
    __tablename__ = "table_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    stroke: Mapped[str] = mapped_column(String(32), nullable=False, default="0.5pt")
    align: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")
    inset: Mapped[str] = mapped_column(String(32), nullable=False, default="5pt")
    fill: Mapped[str] = mapped_column(String(64), nullable=False, default="none")
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="table_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ===========================  NEW ELEMENTS  ================================


# ---------------------------------------------------------------------------
# page  →  #set page(...)
# ---------------------------------------------------------------------------
class PageStyle(Base):
    __tablename__ = "page_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
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
class RawStyle(TextOverrideMixin, Base):
    __tablename__ = "raw_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    tab_size: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    align: Mapped[str] = mapped_column(String(32), nullable=False, default="start")
    theme: Mapped[str] = mapped_column(String(64), nullable=False, default="auto")
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="raw_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# terms  →  #set terms(...)
# ---------------------------------------------------------------------------
class TermsStyle(TextOverrideMixin, Base):
    __tablename__ = "terms_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    tight: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    indent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hanging_indent: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    spacing: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="terms_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# outline  →  #set outline(...)
# ---------------------------------------------------------------------------
class OutlineStyle(TextOverrideMixin, Base):
    __tablename__ = "outline_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    depth: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)
    indent: Mapped[str] = mapped_column(String(32), nullable=False, default="auto")
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="outline_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )


# ---------------------------------------------------------------------------
# equation  →  math.equation — только text override
# ---------------------------------------------------------------------------
class EquationStyle(TextOverrideMixin, Base):
    __tablename__ = "equation_styles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    text_override_style_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("text_override_styles.id", ondelete="SET NULL"),
        nullable=True,
    )

    profile: Mapped[Profile] = relationship(back_populates="equation_style")
    text_override_style: Mapped[Optional["TextOverrideStyle"]] = relationship(
        foreign_keys=[text_override_style_id],
        lazy="joined",
    )
