"""Pydantic schema for per-level heading styles."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models.pydantic.text_override import TextOverrideStyles, TextOverrideStylesUpdate


class HeadingLevelStyles(BaseModel):
    """Стили заголовка по уровню: outlined, bookmarked, offset + text_override."""

    level: int = Field(..., ge=1, le=6)
    outlined: bool = Field(True, description="Отображать в оглавлении")
    bookmarked: Literal["auto", "true", "false"] = Field("auto", description="Закладка в PDF")
    offset: int = Field(0, ge=0, description="Смещение уровня")
    text_override: Optional[TextOverrideStyles] = None


class HeadingLevelStylesUpdate(BaseModel):
    outlined: Optional[bool] = None
    bookmarked: Optional[Literal["auto", "true", "false"]] = None
    offset: Optional[int] = Field(None, ge=0)
    text_override: Optional[TextOverrideStylesUpdate | dict] = None  # None = clear
