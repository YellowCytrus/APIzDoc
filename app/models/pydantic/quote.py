from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models.pydantic.text_override import TextOverrideStyles, TextOverrideStylesUpdate


class QuoteStyles(BaseModel):
    """Стили блока цитаты Typst: #set quote(...)."""

    indent: float = Field(1.5, ge=0.0, description="Отступ в em")
    block: bool = Field(True, description="Блочная цитата")
    quotes: Literal["auto", "true", "false"] = Field(
        "auto",
        description="Кавычки вокруг цитаты",
    )
    text_override: Optional[TextOverrideStyles] = None


class QuoteStylesUpdate(BaseModel):
    indent: Optional[float] = Field(None, ge=0.0)
    block: Optional[bool] = None
    quotes: Optional[Literal["auto", "true", "false"]] = None
    text_override: Optional[TextOverrideStylesUpdate | dict] = None
