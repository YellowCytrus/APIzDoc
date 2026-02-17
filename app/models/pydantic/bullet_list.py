from typing import Literal

from pydantic import BaseModel, Field, field_validator

_DEFAULT_MARKERS = ["- ", "‣", "–"]


class BulletListStyles(BaseModel):
    """Значения по умолчанию в стиле ГОСТ для маркированного списка Typst."""

    tight: bool = True
    marker: list[str] = Field(
        default_factory=lambda: list(_DEFAULT_MARKERS),
        min_length=1,
        max_length=3,
        description="Маркеры для уровней списка",
    )
    indent: float = Field(0.0, ge=0.0, description="Отступ в pt")
    body_indent: float = Field(0.5, ge=0.0, description="Отступ тела в em")
    spacing: Literal["auto", "tight", "loose"] = "auto"

    @field_validator("marker")
    @classmethod
    def pad_markers(cls, v: list[str]) -> list[str]:
        """Дополняет список маркеров до 3 элементов дефолтными значениями."""
        return (v + _DEFAULT_MARKERS)[:3]


class BulletListStylesUpdate(BaseModel):
    tight: bool | None = None
    marker: list[str] | None = Field(None, min_length=1, max_length=3)
    indent: float | None = Field(None, ge=0.0)
    body_indent: float | None = Field(None, ge=0.0)
    spacing: Literal["auto", "tight", "loose"] | None = None

    @field_validator("marker")
    @classmethod
    def pad_markers(cls, v: list[str] | None) -> list[str] | None:
        """Дополняет список маркеров до 3 элементов дефолтными значениями."""
        if v is None:
            return None
        return (v + _DEFAULT_MARKERS)[:3]
