from pydantic import BaseModel, Field


class QuoteStyles(BaseModel):
    """Значения по умолчанию ГОСТ для блока цитаты Typst."""

    indent: float = Field(1.5, ge=0.0, description="Отступ в em")


class QuoteStylesUpdate(BaseModel):
    indent: float | None = Field(None, ge=0.0)
