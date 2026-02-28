"""
Нормализованные ORM-модели стилей элементов.
Каждый тип элемента — отдельная таблица со связью 1:1 к Profile.
Имена колонок совпадают с полями Pydantic DTO для generic маппинга.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


DEFAULT_FONT = "Merriweather"


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
    font: Mapped[str] = mapped_column(String(255), nullable=False, default=DEFAULT_FONT)
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
