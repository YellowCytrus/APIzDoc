from typing import Literal, Optional

from pydantic import BaseModel, Field


class RawStyles(BaseModel):
    """Стили блока кода Typst: #set raw(...)."""

    tab_size: int = Field(2, ge=1, le=16, description="Размер табуляции в пробелах")
    align: str = Field("start", max_length=32, description="Горизонтальное выравнивание")
    theme: str = Field("auto", max_length=64, description="Тема подсветки (auto/none)")


class RawStylesUpdate(BaseModel):
    tab_size: Optional[int] = Field(None, ge=1, le=16)
    align: Optional[str] = Field(None, max_length=32)
    theme: Optional[str] = Field(None, max_length=64)
