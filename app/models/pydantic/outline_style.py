from typing import Optional

from pydantic import BaseModel, Field


class OutlineStyles(BaseModel):
    """Стили оглавления Typst: #set outline(...)."""

    depth: Optional[int] = Field(None, ge=1, description="Глубина (null = все уровни)")
    indent: str = Field("auto", max_length=32, description="Отступ вложенности (auto/длина)")


class OutlineStylesUpdate(BaseModel):
    depth: Optional[int] = Field(None, ge=1)
    indent: Optional[str] = Field(None, max_length=32)
