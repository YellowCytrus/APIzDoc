from typing import Literal, Optional

from pydantic import BaseModel, Field


class QuoteStyles(BaseModel):
    """Стили блока цитаты Typst: #set quote(...)."""

    indent: float = Field(1.5, ge=0.0, description="Отступ в em")
    block: bool = Field(True, description="Блочная цитата")
    quotes: Literal["auto", "true", "false"] = Field(
        "auto", description="Кавычки вокруг цитаты",
    )


class QuoteStylesUpdate(BaseModel):
    indent: Optional[float] = Field(None, ge=0.0)
    block: Optional[bool] = None
    quotes: Optional[Literal["auto", "true", "false"]] = None
