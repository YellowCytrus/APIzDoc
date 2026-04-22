from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.constants.style_defaults import BULLET_MARKERS_DEFAULT, LIST_BODY_INDENT_MM_DEFAULT
from app.models.pydantic.text_override import TextOverrideStyles


class BulletListStyles(BaseModel):
    """Значения по умолчанию в стиле ГОСТ для маркированного списка Typst."""

    tight: bool = True
    marker: list[str] = Field(
        default_factory=lambda: list(BULLET_MARKERS_DEFAULT),
        min_length=1,
        max_length=3,
        description="Маркеры для уровней списка",
    )
    indent: float = Field(0.0, ge=0.0, description="Отступ в mm")
    body_indent: float = Field(LIST_BODY_INDENT_MM_DEFAULT, ge=0.0, description="Отступ тела в mm")
    spacing: Literal["auto", "tight", "loose"] = "auto"
    text_override: Optional[TextOverrideStyles] = None

    @field_validator("marker")
    @classmethod
    def pad_markers(cls, v: list[str]) -> list[str]:
        """Дополняет список маркеров до 3 элементов дефолтными значениями."""
        return (v + BULLET_MARKERS_DEFAULT)[:3]


class BulletListStylesUpdate(BaseModel):
    tight: bool | None = None
    marker: list[str] | None = Field(None, min_length=1, max_length=3)
    indent: float | None = Field(None, ge=0.0)
    body_indent: float | None = Field(None, ge=0.0)
    spacing: Literal["auto", "tight", "loose"] | None = None
    text_override: Optional[TextOverrideStyles | dict] = None

    @field_validator("marker")
    @classmethod
    def pad_markers(cls, v: list[str] | None) -> list[str] | None:
        """Дополняет список маркеров до 3 элементов дефолтными значениями."""
        if v is None:
            return None
        return (v + BULLET_MARKERS_DEFAULT)[:3]
