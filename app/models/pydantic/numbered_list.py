from typing import Literal

from pydantic import BaseModel, Field


class NumberedListStyles(BaseModel):
    """GOST defaults for Typst numbered list."""

    tight: bool = True
    indent: float = Field(0.0, ge=0.0, description="Indent in pt")
    body_indent: float = Field(0.5, ge=0.0, description="Body indent in em")
    spacing: Literal["auto", "tight", "loose"] = "auto"


class NumberedListStylesUpdate(BaseModel):
    tight: bool | None = None
    indent: float | None = Field(None, ge=0.0)
    body_indent: float | None = Field(None, ge=0.0)
    spacing: Literal["auto", "tight", "loose"] | None = None
