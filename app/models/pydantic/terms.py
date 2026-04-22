from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models.pydantic.text_override import TextOverrideStyles, TextOverrideStylesUpdate


class TermsStyles(BaseModel):
    """Стили списка терминов Typst: #set terms(...)."""

    tight: bool = Field(True, description="Компактный список")
    indent: float = Field(0.0, ge=0.0, description="Отступ элемента в mm")
    hanging_indent: float = Field(8.4666666667, ge=0.0, description="Висячий отступ описания в mm")
    spacing: Literal["auto", "tight", "loose"] = "auto"
    text_override: Optional[TextOverrideStyles] = None


class TermsStylesUpdate(BaseModel):
    tight: Optional[bool] = None
    indent: Optional[float] = Field(None, ge=0.0)
    hanging_indent: Optional[float] = Field(None, ge=0.0)
    spacing: Optional[Literal["auto", "tight", "loose"]] = None
    text_override: Optional[TextOverrideStylesUpdate | dict] = None
