"""Pydantic schema for text override styles (element-specific text overrides)."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class TextOverrideStyles(BaseModel):
    """Same fields as DocumentStyles for text, without line_spacing."""

    font: str = Field("libertinus serif", max_length=255)
    font_size: float = Field(12.0, ge=6.0, le=72.0)
    weight: Literal[
        "thin",
        "extralight",
        "light",
        "regular",
        "medium",
        "semibold",
        "bold",
        "extrabold",
        "black",
    ] = "regular"
    style: Literal["normal", "italic", "oblique"] = "normal"
    fill: str = Field("black", max_length=64)
    lang: str = Field("en", max_length=16)
    region: Optional[str] = Field(None, max_length=16)
    tracking: float = Field(0.0)
    word_spacing: float = Field(100.0, ge=0.0, le=500.0)
    hyphenate: Optional[bool] = None
    ligatures: bool = Field(True)
    number_type: Literal["auto", "lining", "old-style"] = "auto"
    number_width: Literal["auto", "proportional", "tabular"] = "auto"


class TextOverrideStylesUpdate(BaseModel):
    font: Optional[str] = Field(None, max_length=255)
    font_size: Optional[float] = Field(None, ge=6.0, le=72.0)
    weight: Optional[
        Literal[
            "thin",
            "extralight",
            "light",
            "regular",
            "medium",
            "semibold",
            "bold",
            "extrabold",
            "black",
        ]
    ] = None
    style: Optional[Literal["normal", "italic", "oblique"]] = None
    fill: Optional[str] = Field(None, max_length=64)
    lang: Optional[str] = Field(None, max_length=16)
    region: Optional[str] = Field(None, max_length=16)
    tracking: Optional[float] = None
    word_spacing: Optional[float] = Field(None, ge=0.0, le=500.0)
    hyphenate: Optional[bool] = None
    ligatures: Optional[bool] = None
    number_type: Optional[Literal["auto", "lining", "old-style"]] = None
    number_width: Optional[Literal["auto", "proportional", "tabular"]] = None
