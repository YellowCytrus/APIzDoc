from typing import Optional

from pydantic import BaseModel, Field


class StrongStyles(BaseModel):
    """Стили жирного текста Typst: #set strong(...)."""

    delta: int = Field(300, ge=0, le=900, description="Дельта веса шрифта")


class StrongStylesUpdate(BaseModel):
    delta: Optional[int] = Field(None, ge=0, le=900)
