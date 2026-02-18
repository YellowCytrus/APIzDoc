from typing import Optional

from pydantic import BaseModel, Field


class HeadingStyles(BaseModel):
    """Стили заголовка Typst: #set heading(...). Только numbering (глобально для всех уровней)."""

    numbering: str = Field("1.1.1", max_length=64, description="Шаблон нумерации или 'none'")


class HeadingStylesUpdate(BaseModel):
    numbering: Optional[str] = Field(None, max_length=64)
