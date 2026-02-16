from typing import Literal

from pydantic import BaseModel, Field


class BulletListStyles(BaseModel):
    """Значения по умолчанию в стиле ГОСТ для маркированного списка Typst."""

    tight: bool = True
    marker: list[str] = Field(
        default_factory=lambda: ["- ", "‣", "–"],
        min_length=1,
        max_length=3,
        description="Маркеры для уровней списка",
    )
    indent: float = Field(0.0, ge=0.0, description="Отступ в pt")
    body_indent: float = Field(0.5, ge=0.0, description="Отступ тела в em")
    spacing: Literal["auto", "tight", "loose"] = "auto"


class BulletListStylesUpdate(BaseModel):
    tight: bool | None = None
    marker: list[str] | None = None
    indent: float | None = Field(None, ge=0.0)
    body_indent: float | None = Field(None, ge=0.0)
    spacing: Literal["auto", "tight", "loose"] | None = None
