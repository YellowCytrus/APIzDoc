from typing import Literal

from pydantic import BaseModel, Field


class BulletListStyles(BaseModel):
    """GOST-style defaults for Typst bullet-list."""

    tight: bool = True
    marker: list[str] = Field(
        default_factory=lambda: ["- ", "‣", "–"],
        min_length=1,
        max_length=3,
        description="Markers for list levels",
    )
    indent: float = Field(0.0, ge=0.0, description="Indent in pt")
    body_indent: float = Field(0.5, ge=0.0, description="Body indent in em")
    spacing: Literal["auto", "tight", "loose"] = "auto"


class BulletListStylesUpdate(BaseModel):
    tight: bool | None = None
    marker: list[str] | None = None
    indent: float | None = Field(None, ge=0.0)
    body_indent: float | None = Field(None, ge=0.0)
    spacing: Literal["auto", "tight", "loose"] | None = None
