from typing import Literal, Optional

from pydantic import BaseModel, Field


class HeadingStyles(BaseModel):
    """Стили заголовка Typst: #set heading(...)."""

    numbering: str = Field("1.1.1", max_length=64, description="Шаблон нумерации или 'none'")
    outlined: bool = Field(True, description="Отображать в оглавлении")
    bookmarked: Literal["auto", "true", "false"] = Field("auto", description="Закладка в PDF")
    offset: int = Field(0, ge=0, description="Смещение уровня")
    hanging_indent: Optional[float] = Field(None, ge=0.0, description="Висячий отступ (null = auto)")


class HeadingStylesUpdate(BaseModel):
    numbering: Optional[str] = Field(None, max_length=64)
    outlined: Optional[bool] = None
    bookmarked: Optional[Literal["auto", "true", "false"]] = None
    offset: Optional[int] = Field(None, ge=0)
    hanging_indent: Optional[float] = Field(None, ge=0.0)
