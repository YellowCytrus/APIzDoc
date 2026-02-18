from typing import Optional

from pydantic import BaseModel, Field

from app.models.pydantic.text_override import TextOverrideStyles, TextOverrideStylesUpdate


class RawStyles(BaseModel):
    """Стили блока кода Typst: #set raw(...)."""

    tab_size: int = Field(2, ge=1, le=16, description="Размер табуляции в пробелах")
    align: str = Field("start", max_length=32, description="Горизонтальное выравнивание")
    theme: str = Field("auto", max_length=64, description="Тема подсветки (auto/none)")
    text_override: Optional[TextOverrideStyles] = None


class RawStylesUpdate(BaseModel):
    tab_size: Optional[int] = Field(None, ge=1, le=16)
    align: Optional[str] = Field(None, max_length=32)
    theme: Optional[str] = Field(None, max_length=64)
    text_override: Optional[TextOverrideStylesUpdate | dict] = None
