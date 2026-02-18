from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models.pydantic.text_override import TextOverrideStyles, TextOverrideStylesUpdate


class FootnoteStyles(BaseModel):
    """Стили сноски Typst: #set footnote(...) + #set footnote.entry(...)."""

    marker_format: Literal["1", "a", "A", "i", "I", "*"] = "1"
    clearance: float = Field(1.0, ge=0.0, description="Расстояние до сносок в em")
    gap: float = Field(0.5, ge=0.0, description="Расстояние между записями в em")
    indent: float = Field(1.0, ge=0.0, description="Отступ записи в em")
    text_override: Optional[TextOverrideStyles] = None


class FootnoteStylesUpdate(BaseModel):
    marker_format: Optional[Literal["1", "a", "A", "i", "I", "*"]] = None
    clearance: Optional[float] = Field(None, ge=0.0)
    gap: Optional[float] = Field(None, ge=0.0)
    indent: Optional[float] = Field(None, ge=0.0)
    text_override: Optional[TextOverrideStylesUpdate | dict] = None
