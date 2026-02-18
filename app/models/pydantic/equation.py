"""Pydantic schema for equation (math) styles."""

from typing import Optional

from pydantic import BaseModel

from app.models.pydantic.text_override import TextOverrideStyles, TextOverrideStylesUpdate


class EquationStyles(BaseModel):
    """Стили формулы Typst: только text_override."""

    text_override: Optional[TextOverrideStyles] = None


class EquationStylesUpdate(BaseModel):
    text_override: Optional[TextOverrideStylesUpdate | dict] = None  # None = clear
